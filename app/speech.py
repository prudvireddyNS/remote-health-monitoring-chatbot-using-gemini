import speech_recognition as sr
import pyttsx3

class SpeechService:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SpeechService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize speech recognition and text-to-speech engines"""
        if self._initialized:
            return
            
        self.recognizer = None
        self.engine = None
        self.speech_available = False
        self.tts_available = False
        
        try:
            # Initialize speech recognition
            self.recognizer = sr.Recognizer()
            # Test microphone availability
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            self.speech_available = True
        except Exception as e:
            print(f"Speech recognition not available: {e}")
        
        try:
            # Initialize text-to-speech engine with proper cleanup
            self._init_tts_engine()
            self.tts_available = True
        except Exception as e:
            print(f"Text-to-speech not available: {e}")
        
        self._initialized = True
    
    def _init_tts_engine(self):
        """Initialize text-to-speech engine with proper error handling"""
        try:
            if self.engine:
                self.engine.endLoop()
                self.engine = None
                
            self.engine = pyttsx3.init('sapi5')
            voices = self.engine.getProperty('voices')
            if not voices:
                raise Exception("No text-to-speech voices found")
            self.engine.setProperty('voice', voices[0].id)  # Default to male voice
            self.engine.setProperty('rate', 150)  # Set default speech rate
            
            # Test TTS with minimal text
            self.engine.say('')
            self.engine.runAndWait()
        except Exception as e:
            self._cleanup()
            raise Exception(f"Failed to initialize text-to-speech engine: {e}")
    
    def _cleanup(self):
        """Clean up resources"""
        if self.engine:
            try:
                self.engine.endLoop()
            except:
                pass
            self.engine = None
    
    def listen(self):
        """Listen to user's speech and convert to text"""
        try:
            with sr.Microphone() as source:
                print("Listening...")
                # Increase timeout and phrase_time_limit for better recognition
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=10)
                print("Processing speech...")
                text = self.recognizer.recognize_google(audio)
                return text
        except sr.WaitTimeoutError:
            return "No speech detected. Please try again."
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand what you said."
        except sr.RequestError as e:
            return f"Could not request results; {e}"
        except Exception as e:
            return f"Error in speech recognition: {e}"
    
    def speak(self, text):
        """Convert text to speech"""
        try:
            if not text or not self.engine:
                return False
            self.engine.say(text)
            self.engine.runAndWait()
            return True
        except Exception as e:
            print(f"Error in text-to-speech: {e}")
            # Try to reinitialize the engine on error
            try:
                self._init_tts_engine()
                self.engine.say(text)
                self.engine.runAndWait()
                return True
            except:
                return False
    
    def set_voice(self, voice_index=0):
        """Set the voice for text-to-speech (0 for male, 1 for female)"""
        try:
            if not self.engine:
                self._init_tts_engine()
            voices = self.engine.getProperty('voices')
            if not voices:
                print("No voices available")
                return False
            if voice_index < len(voices):
                self.engine.setProperty('voice', voices[voice_index].id)
                return True
            return False
        except Exception as e:
            print(f"Error setting voice: {e}")
            return False
    
    def __del__(self):
        """Destructor to ensure proper cleanup"""
        self._cleanup()
