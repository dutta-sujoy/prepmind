from typing import Dict, Any
import io
import tempfile
import os

class VoiceService:
    """
    Voice service using free alternatives:
    - Whisper for Speech-to-Text
    - gTTS for Text-to-Speech
    """
    
    def __init__(self):
        self.whisper_model = None
        self.use_whisper = False
        
        # Try to load Whisper
        try:
            import whisper
            print("Loading Whisper model...")
            self.whisper_model = whisper.load_model("base")
            self.use_whisper = True
            print("✅ Whisper model loaded!")
        except Exception as e:
            print(f"⚠️ Whisper not available: {e}")
            print("Voice features will be limited")
    
    
    def transcribe_audio(self, audio_data: bytes, language_code: str = "en-US") -> Dict[str, Any]:
        """
        Transcribe audio using Whisper
        """
        if not self.use_whisper:
            return {
                "transcript": "[Audio transcription not available - Whisper not loaded]",
                "confidence": 0.0,
                "word_timings": [],
                "error": "Whisper not available"
            }
        
        try:
            import whisper
            import numpy as np
            
            # Save audio to temp file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(audio_data)
                temp_path = tmp.name
            
            # Transcribe
            result = self.whisper_model.transcribe(
                temp_path,
                language=language_code.split("-")[0],
                task="transcribe",
                fp16=False,
                word_timestamps=True
            )
            
            # Clean up
            os.unlink(temp_path)
            
            # Extract word timings
            word_timings = []
            if "segments" in result:
                for segment in result["segments"]:
                    if "words" in segment:
                        for word_info in segment["words"]:
                            word_timings.append({
                                "word": word_info.get("word", "").strip(),
                                "start_time": word_info.get("start", 0),
                                "end_time": word_info.get("end", 0)
                            })
            
            return {
                "transcript": result["text"].strip(),
                "confidence": 0.95,
                "word_timings": word_timings,
                "language": result.get("language", "en"),
                "error": None
            }
            
        except Exception as e:
            print(f"Transcription error: {e}")
            return {
                "transcript": "",
                "confidence": 0.0,
                "word_timings": [],
                "error": str(e)
            }
    
    
    def synthesize_speech(self, text: str, language_code: str = "en-US") -> bytes:
        """
        Convert text to speech using gTTS (free!)
        """
        try:
            from gtts import gTTS
            
            # Create TTS
            tts = gTTS(
                text=text,
                lang=language_code.split("-")[0],
                slow=False
            )
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                temp_path = tmp.name
                tts.save(temp_path)
            
            # Read audio
            with open(temp_path, 'rb') as f:
                audio_data = f.read()
            
            # Clean up
            os.unlink(temp_path)
            
            return audio_data
            
        except Exception as e:
            print(f"TTS error: {e}")
            return b""
    
    
    def analyze_voice_characteristics(self, word_timings: list, transcript: str) -> Dict[str, Any]:
        """
        Analyze voice characteristics from word timings
        """
        if not word_timings:
            return {
                "words_per_minute": 0,
                "filler_words_count": 0,
                "filler_words_percentage": 0,
                "pace": "unknown",
                "confidence_score": 50,
                "total_words": 0,
                "duration_seconds": 0
            }
        
        # Calculate duration
        first_word_start = word_timings[0]["start_time"]
        last_word_end = word_timings[-1]["end_time"]
        duration_seconds = last_word_end - first_word_start
        
        # Words per minute
        total_words = len(word_timings)
        words_per_minute = int((total_words / duration_seconds) * 60) if duration_seconds > 0 else 0
        
        # Detect filler words
        filler_words = ['um', 'uh', 'like', 'you know', 'actually', 'basically', 'literally']
        filler_count = sum(1 for word in word_timings 
                          if word['word'].lower().strip() in filler_words)
        filler_percentage = (filler_count / total_words * 100) if total_words > 0 else 0
        
        # Determine pace
        if words_per_minute < 100:
            pace = "slow"
        elif words_per_minute > 160:
            pace = "fast"
        else:
            pace = "normal"
        
        # Calculate confidence score
        confidence_score = 70  # Base score
        
        if pace == "normal":
            confidence_score += 10
        elif pace == "slow":
            confidence_score -= 5
        else:
            confidence_score -= 10
        
        if filler_percentage < 5:
            confidence_score += 10
        elif filler_percentage > 15:
            confidence_score -= 15
        
        # Check for long pauses
        long_pauses = 0
        for i in range(len(word_timings) - 1):
            gap = word_timings[i + 1]["start_time"] - word_timings[i]["end_time"]
            if gap > 2.0:
                long_pauses += 1
        
        if long_pauses > 3:
            confidence_score -= 10
        
        confidence_score = max(0, min(100, confidence_score))
        
        return {
            "words_per_minute": words_per_minute,
            "filler_words_count": filler_count,
            "filler_words_percentage": round(filler_percentage, 2),
            "pace": pace,
            "long_pauses": long_pauses,
            "confidence_score": confidence_score,
            "total_words": total_words,
            "duration_seconds": round(duration_seconds, 2)
        }


# Singleton instance
voice_service = VoiceService()
