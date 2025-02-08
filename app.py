# app.py
from flask import Flask, render_template, request, send_file
import torch
from transformers import SpeechT5ForTextToSpeech, SpeechT5Processor, SpeechT5HifiGan
from datasets import load_dataset
import soundfile as sf
import uuid
import os

app = Flask(__name__)

# Chargement des modèles une fois au démarrage
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
processor = SpeechT5Processor.from_pretrained("bilalfaye/speecht5_tts-wolof")
model = SpeechT5ForTextToSpeech.from_pretrained("bilalfaye/speecht5_tts-wolof").to(device)
vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan").to(device)
embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
speaker_embedding = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        text = request.json['text']
        filename = f"output_{uuid.uuid4().hex}.wav"
        
        # Génération de la parole
        inputs = processor(text=text, return_tensors="pt", padding=True, truncation=True)
        inputs = {key: value.to(device) for key, value in inputs.items()}
        
        speech = model.generate(
            inputs["input_ids"],
            speaker_embeddings=speaker_embedding.to(device),
            vocoder=vocoder,
            num_beams=7,
            temperature=0.6
        )
        
        # Sauvegarde du fichier audio
        sf.write(filename, speech.detach().cpu().numpy().squeeze(), 16000)
        
        return {'filename': filename}
    
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/audio/<filename>')
def get_audio(filename):
    return send_file(filename, mimetype='audio/wav')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)