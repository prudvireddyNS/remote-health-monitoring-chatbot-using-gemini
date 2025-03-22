'use client';
import { useState, useEffect } from 'react';
import { FaMicrophone, FaStop } from 'react-icons/fa';

export default function VoiceInput({ onTranscriptComplete }) {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    }
  }, []);

  const startListening = () => {
    setError(null);
    try {
      const recognition = new window.SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        setIsListening(true);
        setTranscript('');
      };

      recognition.onresult = (event) => {
        const current = event.resultIndex;
        const transcriptText = event.results[current][0].transcript;
        setTranscript(transcriptText);
        
        if (event.results[current].isFinal) {
          onTranscriptComplete(transcriptText);
          recognition.stop();
        }
      };

      recognition.onerror = (event) => {
        setError(`Error: ${event.error}`);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognition.start();
    } catch (err) {
      setError('Speech recognition is not supported in your browser');
      setIsListening(false);
    }
  };

  const stopListening = () => {
    window.speechRecognition?.stop();
    setIsListening(false);
  };

  return (
    <div className="mt-2">
      <button
        type="button"
        onClick={isListening ? stopListening : startListening}
        className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
          isListening ? 'bg-red-500' : 'bg-blue-500'
        } text-white hover:opacity-90 transition-opacity`}
      >
        {isListening ? (
          <>
            <FaStop /> Stop Recording
          </>
        ) : (
          <>
            <FaMicrophone /> Start Voice Input
          </>
        )}
      </button>
      
      {error && (
        <p className="mt-2 text-sm text-red-500">{error}</p>
      )}
      
      {transcript && (
        <div className="mt-2 p-2 bg-gray-50 border rounded-md">
          <p className="text-sm text-gray-600">Transcript:</p>
          <p className="mt-1">{transcript}</p>
        </div>
      )}
    </div>
  );
}
