from fastapi import APIRouter
from pydantic import BaseModel
from app.agents.agent import run_agent

router = APIRouter()

class ChatRequest(BaseModel):
    session_id: str
    query: str

@router.post("/chat")
def chat(req: ChatRequest):
    response = run_agent(req.query, req.session_id)
    return response
