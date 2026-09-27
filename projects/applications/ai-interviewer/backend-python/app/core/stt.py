"""
Speech-to-text via faster-whisper. Unlike the earlier version, failure is
never silently masked with a canned transcript — callers get an explicit
(transcript, error) pair and decide what to show the user.
"""
print("Loading Whisper for Interviewer...")

_model = None
_load_error = None
try:
    from faster_whisper import WhisperModel
    _model = WhisperModel("base", device="cpu", compute_type="int8")
except Exception as e:
    _load_error = str(e)
    print(f"[stt] Whisper model failed to load: {e}")


def transcribe_audio(path: str):
    """Returns (transcript: str | None, error: str | None).
    Exactly one of the two is populated."""
    if _model is None:
        return None, f"Speech-to-text is unavailable: {_load_error or 'model not loaded'}"
    try:
        segments, _ = _model.transcribe(path, beam_size=5)
        text = " ".join(s.text for s in segments).strip()
        if not text:
            return None, "No speech detected in the recording — try again and speak clearly."
        return text, None
    except Exception as e:
        return None, f"Transcription failed: {e}"
