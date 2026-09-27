"""Speech-to-text via faster-whisper, with an explicit (non-silent) mock fallback."""
import os

_MODEL = None
_LOAD_ERROR = None


def _load_model():
    """Lazily load the Whisper model on first use so import stays fast/cheap."""
    global _MODEL, _LOAD_ERROR
    if _MODEL is not None or _LOAD_ERROR is not None:
        return
    try:
        from faster_whisper import WhisperModel
        size = os.getenv("WHISPER_MODEL", "base")
        _MODEL = WhisperModel(size, device="cpu", compute_type="int8")
        print(f"[stt] faster-whisper '{size}' loaded")
    except Exception as exc:  # pragma: no cover - depends on local install
        _LOAD_ERROR = str(exc)
        print(f"[stt] faster-whisper unavailable ({exc}); STT will report mock results")


def transcribe_audio(file_path: str) -> dict:
    """Transcribe an audio file.

    Returns {"text": str, "mocked": bool} instead of silently returning a fixed
    sentence when the model isn't available — callers (and the UI) can surface
    that a transcription was faked instead of masking the failure.
    """
    _load_model()
    if _MODEL is None:
        return {"text": "[voice input unavailable — Whisper failed to load]", "mocked": True}

    try:
        segments, _info = _MODEL.transcribe(file_path, beam_size=5, language="en")
        text = " ".join(segment.text for segment in segments).strip()
        return {"text": text or "[no speech detected]", "mocked": False}
    except Exception as exc:
        print(f"[stt] transcription error: {exc}")
        return {"text": "[transcription failed]", "mocked": True}
