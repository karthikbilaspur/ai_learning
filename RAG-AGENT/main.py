import os
import shutil
import json
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from orchestrator import orchestrator

# 1. Enable LangSmith Tracing
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "mini-tools-orchestrator"
# Ensure LANGCHAIN_API_KEY is set in your .env or shell environment

app = FastAPI(title="Production AI Agent Orchestrator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 2. File Upload Endpoint
@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"filename": file.filename, "file_path": file_path, "status": "uploaded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 3. Token-by-Token Streaming Endpoint
@app.post("/api/chat/stream")
async def chat_stream(request_data: dict):
    message = request_data.get("message", "")
    file_path = request_data.get("file_path", None)

    full_prompt = message
    if file_path:
        full_prompt += f" [Attached file path: {file_path}]"

    async def event_generator():
        try:
            # Asynchronously stream events from the LangChain orchestrator
            async for chunk in orchestrator.astream({"input": full_prompt}):
                # Check for tool call routing events
                if hasattr(chunk, "tool_calls") and chunk.tool_calls:
                    tool_info = chunk.tool_calls[0]
                    data = {
                        "type": "tool_call",
                        "tool_name": tool_info["name"],
                        "args": tool_info["args"]
                    }
                    yield f"data: {json.dumps(data)}\n\n"
                # Check for direct text streaming content
                elif hasattr(chunk, "content") and chunk.content:
                    data = {
                        "type": "token",
                        "content": chunk.content
                    }
                    yield f"data: {json.dumps(data)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)