# RAG Agent & Multi-Tool AI Platform

A production-grade, containerized AI agent architecture built with **FastAPI**, **LangChain**, and **Next.js**. This platform features a central supervisor orchestrator that dynamically routes user queries to specialized "mini-tools"—ranging from PDF RAG and web scraping to code execution and voice processing.

---

## Architecture Overview

```text
                               ┌───────────────────────────┐
                               │  Next.js 14 Frontend UI   │
                               │   (TypeScript, Tailwind)  │
                               └─────────────┬─────────────┘
                                             │
                                   HTTP SSE / Form-Data
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │    FastAPI API Server     │
                               │        (main.py)          │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │   Master Orchestrator     │
                               │    (orchestrator.py)      │
                               └─────────────┬─────────────┘
                                             │
      ┌──────────────────┬───────────────────┼───────────────────┬──────────────────┐
      ▼                  ▼                   ▼                   ▼                  ▼
┌───────────┐      ┌───────────┐       ┌───────────┐       ┌───────────┐      ┌───────────┐
│ PDF RAG   │      │ Web QA    │       │ CSV Agent │       │ Research  │      │ Voice /   │
│ (01-pdf)  │      │ (02-web)  │       │ (03-csv)  │       │ (06-res)  │      │ Tools     │
└───────────┘      └───────────┘       └───────────┘       └───────────┘      └───────────┘

```

---

## Core Features

* **Master Supervisor Orchestrator**: Uses LLM function binding (`bind_tools`) to route requests to the best underlying agent module dynamically.
* **Specialized Tool Library (`mini-tools/`)**:
* **01-PDF RAG**: Document chunking, embeddings, and vector database querying.
* **02-Web QA**: Live web page scraping and question answering.
* **03-CSV Agent**: Dynamic Pandas dataframe calculations and data extraction.
* **04-Tool Calling**: Exact mathematical computation and weather data fetching.
* **05-Memory Chatbot**: State-aware multi-turn conversational management.
* **06-Research Agent**: Deep multi-source web synthesis and report generation.
* **07-File Organizer**: Local filesystem inspection and automated directory sorting.
* **08-Code Reviewer**: AST parsing and static code analysis for security vulnerabilities.
* **09-Voice Action**: Audio-to-text (Whisper) and text-to-speech execution.

* **Real-time Streaming**: Token-by-token streaming via Server-Sent Events (SSE).
* **Observability**: Built-in tracing using **LangSmith**.
* **Containerized Deployment**: Fully Dockerized setup using `docker-compose`.

---

## Project Structure

```text
├── mini-tools/                 # Modular agent tools (01 to 09)
│   ├── 01-pdf_rag.py
│   ├── 02-website-qa.py
│   ├── 03-csv-data-agent.py
│   ├── 04-Tool-Calling-Agent.py
│   ├── 05-Memory-Chatbot.py
│   ├── 06-research-agent.py
│   ├── 07-file-organizer-agent.py
│   ├── 08-code-reviewer-agent.py
│   └── 09-voice-action-agent.py
├── frontend/                   # Next.js App Router project
│   ├── app/
│   │   └── page.tsx            # Main chat interface with file dropzone
│   ├── Dockerfile
│   └── package.json
├── orchestrator.py             # LangChain routing engine
├── main.py                     # FastAPI REST/SSE server
├── requirements.txt            # Python dependencies
├── Dockerfile.backend          # FastAPI container config
├── docker-compose.yml          # Unified multi-container deployment
└── README.md

```

---

## Getting Started

### Prerequisites

* **Docker & Docker Compose** (Recommended)
* **Python 3.11+** and **Node.js 18+** (For local manual setup)
* **OpenAI API Key**

---

### Environment Setup

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_openai_api_key_here

# Optional: LangSmith Tracing
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=mini-tools-orchestrator

```

---

### Method 1: Run with Docker Compose (Recommended)

To launch both the FastAPI backend and Next.js frontend with one command:

```bash
docker-compose up --build

```

* **Frontend**: `http://localhost:3000`
* **FastAPI Backend**: `http://localhost:8000`
* **API Documentation**: `http://localhost:8000/docs`

---

### Method 2: Manual Local Development

#### 1. Backend Setup (FastAPI)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install fastapi uvicorn python-multipart langsmith

# Start API server
python main.py

```

#### 2. Frontend Setup (Next.js)

In a separate terminal window:

```bash
cd frontend

# Install Node modules
npm install

# Run dev server
npm run dev

```

Visit `http://localhost:3000` to interact with the system.

---

## API Endpoints

| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/chat/stream` | `POST` | Streams orchestrator reasoning and response tokens via SSE. |
| `/api/upload` | `POST` | Accepts file uploads (`.pdf`, `.csv`, `.mp3`) for tool processing. |
| `/docs` | `GET` | Interactive Swagger API documentation. |

---

## License

Distributed under the MIT License. See `LICENSE` for more information.
