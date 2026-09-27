"""Text-to-speech via Piper, falling back to a short silent WAV if unavailable."""
import os
import wave

SAMPLE_RATE = 22050


def _write_silence(output_path: str, seconds: float = 0.5) -> None:
    with wave.open(output_path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b"\x00\x00" * int(SAMPLE_RATE * seconds))


def synthesize_speech(text: str, output_path: str) -> dict:
    """Synthesize `text` to a WAV file at `output_path`.

    Returns {"path": str, "mocked": bool} so callers know when audio is real
    speech versus a silent placeholder (Piper missing or misconfigured).
    """
    voice_path = os.getenv("PIPER_VOICE", "en_US-lessac-medium.onnx")
    try:
        from piper import PiperVoice

        if not os.path.exists(voice_path):
            raise FileNotFoundError(f"Piper voice model not found at '{voice_path}'")

        voice = PiperVoice.load(voice_path)
        with open(output_path, "wb") as f:
            for audio in voice.synthesize(text):
                f.write(audio.audio_int16_bytes)
        return {"path": output_path, "mocked": False}
    except Exception as exc:
        print(f"[tts] Piper unavailable ({exc}); writing silent placeholder")
        try:
            _write_silence(output_path)
        except Exception as inner_exc:
            print(f"[tts] failed to write placeholder audio: {inner_exc}")
            open(output_path, "wb").close()
        return {"path": output_path, "mocked": True}
