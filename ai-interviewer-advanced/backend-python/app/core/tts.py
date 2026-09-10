"""
Text-to-speech via Piper. If Piper (or its voice model) isn't available,
this returns None rather than writing a silent .wav that pretends to be
real audio — the caller then omits audio_url and the frontend genuinely
falls back to the browser's SpeechSynthesis API instead of playing silence.
"""
import os


def synthesize_speech(text: str, out_path: str):
    """Returns out_path on success, or None on failure."""
    try:
        from piper import PiperVoice
        voice_path = os.getenv("PIPER_VOICE", "en_US-lessac-medium.onnx")
        if not os.path.exists(voice_path):
            print(f"[tts] Piper voice model not found at {voice_path} — falling back to browser TTS.")
            return None
        voice = PiperVoice.load(voice_path)
        with open(out_path, "wb") as f:
            for audio in voice.synthesize(text):
                f.write(audio.audio_int16_bytes)
        return out_path
    except Exception as e:
        print(f"[tts] Piper synthesis failed, falling back to browser TTS: {e}")
        return None
