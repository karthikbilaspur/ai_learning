from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import uuid

from .core.stt import transcribe_audio
from .core.interviewer_graph import create_interviewer_graph, get_question_bank, graph_backend_status
from .core.tts import synthesize_speech
from .core import memory as memory_store

app = FastAPI(title="AI Interviewer Advanced")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
os.makedirs("static/audio", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

graph = create_interviewer_graph()
question_bank = get_question_bank()


class StartReq(BaseModel):
    role: str
    level: str
    session_id: str | None = None


@app.get("/")
def health():
    return {"status": "Interviewer online"}


@app.get("/status")
def status():
    """Honest capability report — what's actually active, not aspirational."""
    return graph_backend_status()


@app.get("/memory")
def memory(session_id: str):
    return memory_store.get_memory(session_id)


def _maybe_tts(text: str):
    audio_filename = f"{uuid.uuid4()}.wav"
    audio_path = f"static/audio/{audio_filename}"
    result = synthesize_speech(text, audio_path)
    return f"/static/audio/{audio_filename}" if result else None


@app.post("/start")
def start(req: StartReq):
    session_id = req.session_id or str(uuid.uuid4())
    mem = memory_store.get_memory(session_id)
    state = {
        "role": req.role,
        "level": req.level,
        "session_id": session_id,
        "memory": mem,
        "asked_ids": mem["asked_question_ids"],
    }
    result = graph.invoke(state)
    q = result["current_question"]
    memory_store.record_question_asked(session_id, q["question_id"])
    q["audio_url"] = _maybe_tts(q["question_text"])
    q["session_id"] = session_id
    return q


@app.post("/answer")
async def answer(
    file: UploadFile = File(...),
    question_id: str = Form(...),
    role: str = Form(...),
    level: str = Form(...),
    session_id: str = Form(...),
):
    tmp = f"/tmp/{uuid.uuid4()}.webm"
    with open(tmp, "wb") as f:
        f.write(await file.read())

    transcript, stt_error = transcribe_audio(tmp)
    os.remove(tmp) if os.path.exists(tmp) else None

    if stt_error:
        # Fail loudly and specifically instead of silently faking a transcript.
        raise HTTPException(status_code=502, detail=stt_error)

    mem = memory_store.get_memory(session_id)
    state = {
        "role": role,
        "level": level,
        "session_id": session_id,
        "question_id": question_id,
        "transcript": transcript,
        "memory": mem,
        "asked_ids": mem["asked_question_ids"],
    }
    result = graph.invoke(state)

    evaluation = result["evaluation"]
    next_q = result.get("next_question")

    new_memory = memory_store.update_memory(session_id, transcript, evaluation, evaluation["category"])

    if next_q:
        memory_store.record_question_asked(session_id, next_q["question_id"])
        next_q["audio_url"] = _maybe_tts(next_q["question_text"])
        next_q["session_id"] = session_id

    return {
        "transcript": transcript,
        "evaluation": evaluation,
        "next_question": next_q,
        "memory": new_memory,
    }
