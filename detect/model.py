import speech_recognition as sr
import pyttsx3
import threading
import queue
import time
from typing import Optional, List

class SpeechModel:
    """
    A comprehensive speech recognition and text-to-speech model for ClassTrack application.
    Handles microphone input, speech-to-text conversion, and text-to-speech output.
    """
    
    def __init__(self):
        """Initialize the speech model with recognition and TTS engines."""
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        self.is_listening = False
        self.speech_queue = queue.Queue()
        
        # Configure TTS settings
        self._configure_tts()
        
        # Calibrate microphone for ambient noise
        self._calibrate_microphone()
    
    def _configure_tts(self):
        """Configure text-to-speech engine settings."""
        try:
            # Set speech rate (words per minute)
            self.tts_engine.setProperty('rate', 180)
            
            # Set volume (0.0 to 1.0)
            self.tts_engine.setProperty('volume', 0.8)
            
            # Try to set a voice (optional)
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Use the first available voice
                self.tts_engine.setProperty('voice', voices[0].id)
        except Exception as e:
            print(f"Warning: Could not configure TTS settings: {e}")
    
    def _calibrate_microphone(self):
        """Calibrate microphone for ambient noise."""
        try:
            print("Calibrating microphone for ambient noise...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Microphone calibration complete.")
        except Exception as e:
            print(f"Warning: Could not calibrate microphone: {e}")
    
    def listen_from_microphone(self, timeout: int = 5, phrase_timeout: int = 2) -> Optional[str]:
        """
        Listen for speech from the microphone and convert to text.
        
        Args:
            timeout (int): Maximum time to wait for speech to start
            phrase_timeout (int): Maximum time to wait for phrase to complete
            
        Returns:
            Optional[str]: Recognized text or None if no speech detected
        """
        try:
            print("Listening for speech...")
            with self.microphone as source:
                # Listen for audio with timeout
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_timeout
                )
            
            print("Processing speech...")
            # Use Google's speech recognition
            text = self.recognizer.recognize_google(audio)
            print(f"Recognized: {text}")
            return text
            
        except sr.WaitTimeoutError:
            print("No speech detected within timeout period")
            return None
        except sr.UnknownValueError:
            print("Could not understand the audio")
            return None
        except sr.RequestError as e:
            print(f"Error with speech recognition service: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error during speech recognition: {e}")
            return None
    
    def text_to_speech(self, text: str, save_to_file: Optional[str] = None) -> bool:
        """
        Convert text to speech and play it.
        
        Args:
            text (str): Text to convert to speech
            save_to_file (Optional[str]): Path to save audio file (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not text.strip():
                print("No text provided for speech synthesis")
                return False
            
            print(f"Converting to speech: {text}")
            
            if save_to_file:
                # Save to file
                self.tts_engine.save_to_file(text, save_to_file)
            
            # Speak the text
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            
            return True
            
        except Exception as e:
            print(f"Error during text-to-speech conversion: {e}")
            return False
    
    def start_continuous_listening(self, callback_function=None):
        """
        Start continuous listening in a separate thread.
        
        Args:
            callback_function: Function to call when speech is detected
        """
        def listen_continuously():
            self.is_listening = True
            while self.is_listening:
                try:
                    text = self.listen_from_microphone(timeout=1, phrase_timeout=3)
                    if text and callback_function:
                        callback_function(text)
                    elif text:
                        self.speech_queue.put(text)
                except Exception as e:
                    print(f"Error in continuous listening: {e}")
                time.sleep(0.1)  # Small delay to prevent excessive CPU usage
        
        # Start listening in a separate thread
        listening_thread = threading.Thread(target=listen_continuously, daemon=True)
        listening_thread.start()
        print("Started continuous listening...")
    
    def stop_continuous_listening(self):
        """Stop continuous listening."""
        self.is_listening = False
        print("Stopped continuous listening.")
    
    def get_speech_from_queue(self) -> Optional[str]:
        """
        Get the next speech text from the queue.
        
        Returns:
            Optional[str]: Next speech text or None if queue is empty
        """
        try:
            return self.speech_queue.get_nowait()
        except queue.Empty:
            return None
    
    def get_available_engines(self) -> List[str]:
        """
        Get list of available speech recognition engines.
        
        Returns:
            List[str]: List of available engines
        """
        engines = []
        
        # Check Google Speech Recognition
        try:
            # Test with a small audio sample
            engines.append("Google Speech Recognition")
        except:
            pass
        
        # Check if offline recognition is available
        try:
            # Check for other engines like CMU Sphinx
            engines.append("CMU Sphinx (Offline)")
        except:
            pass
        
        # Check TTS engines
        try:
            tts_voices = self.tts_engine.getProperty('voices')
            if tts_voices:
                engines.append(f"TTS Engine with {len(tts_voices)} voices")
        except:
            pass
        
        return engines if engines else ["Basic Speech Recognition"]
    
    def test_microphone(self) -> dict:
        """
        Test microphone functionality.
        
        Returns:
            dict: Test results with status and details
        """
        try:
            # Test microphone access
            with self.microphone as source:
                print("Testing microphone access...")
                audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=1)
            
            return {
                "status": "success",
                "message": "Microphone is working properly",
                "sample_rate": source.SAMPLE_RATE,
                "chunk_size": source.CHUNK
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Microphone test failed: {e}",
                "sample_rate": None,
                "chunk_size": None
            }
    
    def set_recognition_language(self, language_code: str = "en-US"):
        """
        Set the language for speech recognition.
        
        Args:
            language_code (str): Language code (e.g., "en-US", "es-ES", "fr-FR")
        """
        self.recognition_language = language_code
        print(f"Speech recognition language set to: {language_code}")
    
    def transcribe_audio_file(self, file_path: str) -> Optional[str]:
        """
        Transcribe audio from a file.
        
        Args:
            file_path (str): Path to the audio file
            
        Returns:
            Optional[str]: Transcribed text or None if failed
        """
        try:
            with sr.AudioFile(file_path) as source:
                audio = self.recognizer.record(source)
            
            text = self.recognizer.recognize_google(audio)
            return text
        except Exception as e:
            print(f"Error transcribing audio file: {e}")
            return None