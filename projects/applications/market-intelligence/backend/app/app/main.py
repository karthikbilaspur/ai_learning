import json
import asyncio
from fastapi import FastAPI, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlmodel import Session, select

from app.core.db import init_db, get_session
from app.models.research import ResearchRun
from app.agent.graph import app_graph
from app.services.pdf import generate_pdf_report

app = FastAPI(title="Market Intelligence Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

class ResearchRequest(BaseModel):
    company_name: str

class PDFExportRequest(BaseModel):
    company_name: str
    markdown_content: str

@app.post("/api/research/stream")
async def stream_research(request: ResearchRequest, db: Session = Depends(get_session)):
    """Streams research updates via SSE and persists the final result in SQLite."""
    async def event_generator():
        initial_state = {
            "company_name": request.company_name,
            "search_queries": [],
            "scraped_documents": [],
            "structured_data": None,
            "critique_feedback": None,
            "final_report": None,
            "search_retry_count": 0
        }

        final_data = None
        final_report = ""

        for output in app_graph.stream(initial_state):
            for node_name, state_update in output.items():
                if "structured_data" in state_update:
                    final_data = state_update["structured_data"]
                if "final_report" in state_update and state_update["final_report"]:
                    final_report = state_update["final_report"]

                yield f"data: {json.dumps({'node': node_name, 'update': state_update}, default=str)}\n\n"
                await asyncio.sleep(0.1)

        # Database Persistence
        if final_report:
            db_run = ResearchRun(
                company_name=request.company_name,
                structured_data=json.dumps(final_data) if final_data else None,
                final_report=final_report
            )
            db.add(db_run)
            db.commit()

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/api/research/history")
def get_research_history(db: Session = Depends(get_session)):
    """Retrieves all past research runs from SQLite database."""
    runs = db.exec(select(ResearchRun).order_by(ResearchRun.created_at.desc())).all()
    return runs

@app.post("/api/research/export-pdf")
def export_pdf(request: PDFExportRequest):
    """Generates and downloads a formatted PDF report."""
    pdf_buffer = generate_pdf_report(request.company_name, request.markdown_content)
    return Response(
        content=pdf_buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={request.company_name}_report.pdf"}
    )