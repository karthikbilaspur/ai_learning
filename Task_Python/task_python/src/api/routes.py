
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, TaskLog
from ..auth import get_current_user, hash_password, verify_password, create_access_token
from ..schemas import UserCreate, TokenResponse, ToolRequest
from ..agent.core import AgentOrchestrator
from fastapi.security import OAuth2PasswordRequestForm
import structlog

router = APIRouter()
logger = structlog.get_logger()
orchestrator = AgentOrchestrator()

@router.post("/auth/register", tags=["auth"])
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username==payload.username).first():
        raise HTTPException(400, "Username exists")
    user = User(username=payload.username, email=payload.email, hashed_password=hash_password(payload.password))
    db.add(user); db.commit(); db.refresh(user)
    logger.info("user_registered", username=user.username)
    return {"id": user.id, "username": user.username}

@router.post("/auth/login", response_model=TokenResponse, tags=["auth"])
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username==form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    token = create_access_token({"sub": user.username})
    return {"access_token": token}

@router.post("/agent/run", tags=["agent"])
def run_tool(req: ToolRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        execution = orchestrator.execute(req.tool, req.params)
        log = TaskLog(user_id=current_user.id, tool_name=req.tool, input_params=req.params, output_summary=str(execution["result"])[:2000], status="success", duration_ms=execution["duration_ms"])
        db.add(log); db.commit()
        return {"tool": req.tool, "status": "success", **execution}
    except Exception as e:
        log = TaskLog(user_id=current_user.id, tool_name=req.tool, input_params=req.params, output_summary=str(e), status="failed")
        db.add(log); db.commit()
        raise HTTPException(400, str(e))

@router.get("/agent/tools", tags=["agent"])
def list_tools(user: User = Depends(get_current_user)):
    return {"tools": ["reddit_analysis","reddit_flair","meme_scrapper","rename_files","rename_with_time","rescale_image","restaurant","reverse_tower","tower_defense"]}

@router.get("/logs", tags=["monitoring"])
def get_logs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logs = db.query(TaskLog).filter(TaskLog.user_id==current_user.id).order_by(TaskLog.created_at.desc()).limit(50).all()
    return logs
