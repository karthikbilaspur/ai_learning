A local-first voice assistant: talk to it, it transcribes you with Whisper, thinks with a local Ollama LLM, can call a few tools (including Google Calendar), and talks back with Piper TTS — all running on your machine.


Architecture

Three services, talking over REST/WebSocket:

frontend/ (React + Vite) — hold-to-talk voice console, session memory panel, waveform visualizer. Connects to the gateway over Socket.IO.
backend-node/ (Express + Socket.IO) — the gateway. Receives audio over a WebSocket, forwards it to the Python service, persists conversation memory to a local JSON file, and proxies Google Calendar OAuth + events.
backend-python/ (FastAPI) — the "brain." Runs speech-to-text (faster-whisper), calls the local LLM (Ollama, llama3.1:8b by default), parses tool calls out of the model's response, and runs text-to-speech (Piper).

All AI inference runs locally. The only outbound call is a weather lookup (wttr.in) and, if you connect it, the Google Calendar API.

Tools the LLM can call
Tool	What it does
get_time	Current local time (answered without hitting the LLM)
get_weather(city)	Live weather via wttr.in
tell_joke	Random joke from a small local list
remember_note(text)	Appends a note to a local JSON file
list_events_today	Reads today's Google Calendar events
create_event(title, start, end, ...)	Creates a Google Calendar event

Tool calls are parsed out of the model's raw response by scanning brace depth (not a naive regex), so replies that mix prose and a JSON tool call, or contain stray {} elsewhere in the text, still parse correctly.

What's real vs. mocked

The backend is explicit about degraded states instead of hiding them:

If Whisper fails to load, /process-voice returns a marker transcript and transcript_mocked: true — not a fake sentence pretending to be a real transcription.
If Piper (or its voice model) isn't available, a short silent .wav is written instead and audio_mocked: true is returned, so the frontend (or you) can tell real speech from a placeholder.
If Ollama is unreachable, the assistant replies with an explicit "my local language model is unavailable" message rather than staying silent or crashing.
Calendar tools return "Google Calendar is not connected yet" until you complete the OAuth flow — they don't fail silently.
Setup

You'll need three terminals (and Ollama running separately).

1. Python brain

bash
cd backend-python
cp .env
pip install -r requirements.txt
uvicorn app.main:app --port 8000 --reload

2. Node gateway

bash
cd backend-node
cp .env
npm install
npm run dev

3. Frontend

bash
cd frontend
cp .env
npm install
npm run dev

4. Ollama (separately, once)

bash
ollama pull llama3.1:8b
ollama serve

Open http://localhost:5173, hold the talk button, speak, release.

Optional for full local voice: PIPER_VOICE=/path/to/voice.onnx + pip install piper-tts. Without it, TTS falls back to a silent audio placeholder (see "What's real vs. mocked" above).

Google Calendar

Create OAuth credentials in Google Cloud Console (Calendar API enabled), set GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET in backend-node/.env, then click "Connect calendar" in the UI. Tokens are stored in a single flat file (backend-node/data/google-tokens.json) — this is single-user by design, not multi-tenant safe.

Tests
bash
cd backend-python
pytest tests/

Covers tool-call parsing (including brace-matching edge cases) and the local tools (get_time, tell_joke, remember_note).

Known limitations
Single-user only — one shared memory file, one shared calendar token file, no auth between the frontend and gateway.
CORS defaults to * on the Python service — fine on a trusted local network, tighten ALLOWED_ORIGINS before exposing it elsewhere.
No containerization — three services to start by hand.
SERVICE_API_KEY (Python) auth is opt-in and off by default.
