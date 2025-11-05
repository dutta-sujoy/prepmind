from typing import Dict, Any
import io
import tempfile
import os


class VoiceService:
    """
    Voice service using free alternatives:
    - Whisper for Speech-to-Text (requires ffmpeg)
    - Edge-TTS for realistic interviewer Text-to-Speech (neural voices)
    """

    def __init__(self):
        self.whisper_model = None
        self.use_whisper = False

        # Initialize Whisper (STT)
        try:
            import whisper
            print("Loading Whisper model...")
            self.whisper_model = whisper.load_model("base")
            self.use_whisper = True
            print("✅ Whisper model loaded!")
        except Exception as e:
            print(f"⚠️ Whisper not available: {e}")
            print("Voice features will be limited (install ffmpeg and whisper)")

    def transcribe_audio(self, audio_data: bytes, language_code: str = "en-US") -> Dict[str, Any]:
        """
        Transcribe audio using Whisper.
        Returns transcript and basic metadata. Word timings are not provided by default.
        """
        print(f"📝 Received audio for transcription: {len(audio_data)} bytes")

        if not self.use_whisper or self.whisper_model is None:
            return {
                "transcript": "",
                "confidence": 0.0,
                "word_timings": [],
                "error": "Whisper not available. Please install ffmpeg and the whisper package."
            }

        try:
            # Write bytes to a temporary file for whisper to read
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                temp_path = tmp.name
                tmp.write(audio_data)

            # Language: use primary part like 'en'
            lang = (language_code or "en-US").split("-")[0]

            # Transcribe (fp16 False for CPU)
            result = self.whisper_model.transcribe(
                temp_path, language=lang, fp16=False)

            # Clean up temp file
            try:
                os.unlink(temp_path)
            except Exception:
                pass

            transcript_text = result.get("text", "").strip()

            return {
                "transcript": transcript_text,
                "confidence": 0.0,  # Whisper does not provide a single confidence score
                "word_timings": [],  # Not available with default whisper
                "error": None
            }
        except Exception as e:
            return {
                "transcript": "",
                "confidence": 0.0,
                "word_timings": [],
                "error": f"Transcription error: {e}"
            }

    def synthesize_speech(self, text: str, language_code: str = "en-US") -> bytes:
        """
        Convert text to speech using Edge-TTS neural voices for a realistic interviewer tone.
        Uses the edge_tts Python API executed in a dedicated thread event loop (no CLI required).
        """
        try:
            import asyncio
            from threading import Thread
            import edge_tts

            # Choose a professional interviewer-style voice by locale
            lang = (language_code or "en-US").lower()
            voice_by_lang = {
                "en-us": "en-US-GuyNeural",      # neutral professional male
                "en-gb": "en-GB-RyanNeural",     # British male
                "en-in": "en-IN-PrabhatNeural",  # Indian male
                "en-au": "en-AU-WilliamNeural",
            }
            voice = voice_by_lang.get(lang, "en-US-GuyNeural")

            # Prepare temp output path
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                out_path = tmp.name

            async def _synthesize_async():
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(out_path)

            # Run the coroutine in a separate thread with its own event loop
            exc: Dict[str, Any] = {}

            def _runner():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(_synthesize_async())
                except Exception as e:
                    exc["e"] = e
                finally:
                    try:
                        loop.close()
                    except Exception:
                        pass

            t = Thread(target=_runner)
            t.start()
            t.join()

            if "e" in exc:
                raise exc["e"]

            # Read audio bytes
            with open(out_path, 'rb') as f:
                audio_data = f.read()

            try:
                os.unlink(out_path)
            except Exception:
                pass

            return audio_data
        except ModuleNotFoundError:
            print(
                "TTS error: edge_tts is not installed. Please run: pip install edge-tts")
            return b""
        except Exception as e:
            print(f"TTS error (edge_tts): {e}")
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
        words_per_minute = int(
            (total_words / duration_seconds) * 60) if duration_seconds > 0 else 0

        # Detect filler words
        filler_words = ['um', 'uh', 'like', 'you know',
                        'actually', 'basically', 'literally']
        filler_count = sum(1 for word in word_timings
                           if word['word'].lower().strip() in filler_words)
        filler_percentage = (filler_count / total_words *
                             100) if total_words > 0 else 0

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
            gap = word_timings[i + 1]["start_time"] - \
                word_timings[i]["end_time"]
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
