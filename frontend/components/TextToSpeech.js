'use client';
import { useState, useEffect } from 'react';
import { FaPlay, FaStop, FaPause } from 'react-icons/fa';

export default function TextToSpeech({ text }) {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [utterance, setUtterance] = useState(null);
  const [voices, setVoices] = useState([]);
  const [femaleVoice, setFemaleVoice] = useState(null);
  const [isFemaleVoice, setIsFemaleVoice] = useState(true);  // Add this line

  useEffect(() => {
    const synth = window.speechSynthesis;
    
    // Force voices to load
    synth.getVoices();

    const loadVoices = () => {
      const availableVoices = synth.getVoices();
      const englishVoices = availableVoices.filter(voice => voice.lang.includes('en'));
      setVoices(englishVoices);
      
      // Pre-select a default voice
      const defaultVoice = englishVoices.find(voice => 
        voice.name.toLowerCase().includes('female')
      );
      if (defaultVoice) {
        setIsFemaleVoice(true);
      }
    };

    loadVoices();
    
    // Handle voice loading in Chrome
    if (speechSynthesis.onvoiceschanged !== undefined) {
      speechSynthesis.onvoiceschanged = loadVoices;
    }

    // Cleanup
    return () => {
      synth.cancel();
    };
  }, []);

  useEffect(() => {
    if (!text || voices.length === 0) return;
    
    const synth = window.speechSynthesis;
    const u = new SpeechSynthesisUtterance(text);
    
    // Find female voice
    let selectedVoice = voices.find(voice => 
      voice.name.toLowerCase().includes('female')
    );
    
    // Fallback to any English voice if female voice not found
    if (!selectedVoice) {
      selectedVoice = voices[0];
    }
    
    u.voice = selectedVoice;
    u.pitch = 1.2; // Higher pitch for female voice
    u.rate = 1.0;
    
    u.onend = () => {
      setIsSpeaking(false);
      setIsPaused(false);
    };

    setUtterance(u);
  }, [text, voices, isFemaleVoice]);

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
      synth.cancel(); // Clear any existing speech
      if (utterance) {
        // Ensure voice is set before speaking
        const currentVoice = voices.find(voice => 
          voice.name.toLowerCase().includes('female')
        ) || voices[0];
        utterance.voice = currentVoice;
        synth.speak(utterance);
        setIsSpeaking(true);
        setIsPaused(false);
      }
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
