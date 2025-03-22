'use client';
import { useState, useEffect } from 'react';
import { FaPlay, FaStop, FaPause } from 'react-icons/fa';

export default function TextToSpeech({ text }) {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [utterance, setUtterance] = useState(null);
  const [voice, setVoice] = useState(null);

  useEffect(() => {
    const synth = window.speechSynthesis;
    const u = new SpeechSynthesisUtterance(text);
    
    // Get available voices and set a female English voice
    const voices = synth.getVoices();
    // Try to find a female English voice
    const femaleVoice = voices.find(voice => 
      voice.lang.includes('en') && voice.name.toLowerCase().includes('female')
    ) || // Fallback to Microsoft Zira or any other female voice
    voices.find(voice => 
      voice.name.includes('Zira') || voice.name.toLowerCase().includes('female')
    ) || // Final fallback to any English voice
    voices.find(voice => voice.lang.includes('en'));
    
    if (femaleVoice) {
      u.voice = femaleVoice;
      // Set a slightly higher pitch for more feminine voice
      u.pitch = 1.2;
      u.rate = 1.0;
    }
    
    u.onend = () => {
      setIsSpeaking(false);
      setIsPaused(false);
    };

    setUtterance(u);
    
    return () => {
      synth.cancel();
    };
  }, [text]);

  const toggleSpeech = () => {
    const synth = window.speechSynthesis;

    if (isSpeaking) {
      if (isPaused) {
        synth.resume();
        setIsPaused(false);
      } else {
        synth.pause();
        setIsPaused(true);
      }
    } else {
      synth.cancel();
      synth.speak(utterance);
      setIsSpeaking(true);
      setIsPaused(false);
    }
  };

  const stopSpeech = () => {
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
    setIsPaused(false);
  };

  if (!utterance) return null;

  return (
    <div className="flex items-center gap-2 mt-4">
      <button
        onClick={toggleSpeech}
        className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
          isSpeaking ? 'bg-yellow-500' : 'bg-green-500'
        } text-white hover:opacity-90 transition-opacity`}
      >
        {isSpeaking && isPaused ? (
          <>
            <FaPlay /> Resume
          </>
        ) : isSpeaking ? (
          <>
            <FaPause /> Pause
          </>
        ) : (
          <>
            <FaPlay /> Read Aloud
          </>
        )}
      </button>
      
      {isSpeaking && (
        <button
          onClick={stopSpeech}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-red-500 text-white hover:opacity-90 transition-opacity"
        >
          <FaStop /> Stop
        </button>
      )}
    </div>
  );
}
