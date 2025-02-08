import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";

export default function TranslatorApp() {
  const [text, setText] = useState("");
  const [translation, setTranslation] = useState("");
  const [audioSrc, setAudioSrc] = useState(null);

  const translateText = async () => {
    const response = await fetch("http://localhost:5000/translate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    const data = await response.json();
    setTranslation(data.translation);
  };

  const generateSpeech = async () => {
    const response = await fetch("http://localhost:5000/tts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: translation }),
    });
    const audioBlob = await response.blob();
    setAudioSrc(URL.createObjectURL(audioBlob));
  };

  return (
    <div className="p-6 max-w-lg mx-auto">
      <Card>
        <CardContent className="p-4">
          <Input
            type="text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Entrez un texte"
            className="mb-4"
          />
          <Button onClick={translateText} className="mr-2">Traduire</Button>
          <Button onClick={generateSpeech} disabled={!translation}>Écouter</Button>
          {translation && <p className="mt-4">Traduction : {translation}</p>}
          {audioSrc && <audio controls src={audioSrc} className="mt-4" />}
        </CardContent>
      </Card>
    </div>
  );
}
