import matplotlib.pyplot as plt

# Define the diagram text
diagram_text = """
===================================================================================
                  PRODUCTION AI AGENT PLATFORM ARCHITECTURE
===================================================================================

 [ USER INTERACTION LAYER ]
 +-------------------------------------------------------------------------------+
 |                              Next.js 14 Frontend                              |
 |   - Interactive Chat UI              - Real-Time Token Streaming (SSE)        |
 |   - Drag-and-Drop File Uploader      - Multi-Format Display (Code/Audio)      |
 +-------------------------------------------------------------------------------+
                                        |
                                        | HTTP / SSE Stream
                                        v
 [ API & TRANSPORT LAYER ]
 +-------------------------------------------------------------------------------+
 |                              FastAPI Gateway                                  |
 |   - POST /api/chat/stream            - File Ingestion (/api/upload)           |
 |   - CORS Middleware                  - Error & Payload Formatting             |
 +-------------------------------------------------------------------------------+
                                        |
                                        | Invokes Router
                                        v
 [ ORCHESTRATION LAYER ]
 +-------------------------------------------------------------------------------+
 |                         Master Supervisor Orchestrator                        |
 |                           (orchestrator.py - LangChain)                       |
 |                                                                               |
 |   Decides intent -> Dynamically routes to the right tool using `bind_tools`   |
 +-------------------------------------------------------------------------------+
                                        |
                 +----------------------+----------------------+
                 |                      |                      |
                 v                      v                      v
 [ SPECIALIZED TOOL LAYER - `mini-tools/` ]
 +-----------------------+  +-----------------------+  +-----------------------+
 | 01. PDF RAG           |  | 04. Tool Calling      |  | 07. File Organizer    |
 | (FAISS / PyPDF)       |  | (Math & Weather)      |  | (FS Directory Ops)    |
 +-----------------------+  +-----------------------+  +-----------------------+
 | 02. Web QA            |  | 05. Memory Chatbot    |  | 08. Code Reviewer     |
 | (BS4 / FAISS)         |  | (Conversation State)  |  | (AST Code Audit)      |
 +-----------------------+  +-----------------------+  +-----------------------+
 | 03. CSV Data Agent    |  | 06. Research Agent    |  | 09. Voice Agent       |
 | (Pandas Code Exec)    |  | (Tavily Web Synthesis)|  | (Whisper STT / TTS)   |
 +-----------------------+  +-----------------------+  +-----------------------+
                                        |
                                        v
 [ OBSERVABILITY & INFRASTRUCTURE LAYER ]
 +-------------------------------------------------------------------------------+
 |  LangSmith Tracing  |  Docker & Docker Compose  |  OpenAI API (GPT-4o)       |
 |  (Latency & Audit)  |  (Unified Deployment)     |  (LLM Engine)              |
 +-------------------------------------------------------------------------------+
===================================================================================
"""

# Render as image
fig, ax = plt.subplots(figsize=(12, 14), facecolor='#0f172a')
ax.set_facecolor('#0f172a')
ax.axis('off')

ax.text(0.02, 0.98, diagram_text, color='#38bdf8', fontfamily='monospace',
        fontsize=10, va='top', ha='left')

plt.tight_layout()
plt.savefig("infographic.png", dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
print("Successfully generated infographic.png!")