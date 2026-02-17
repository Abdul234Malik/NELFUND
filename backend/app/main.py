import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# ✅ import the compiled LangGraph agent from graph.py
from app.agents.graph import agent

app = FastAPI()

# 🔓 Allow frontend access (dev + production)
# In production, set FRONTEND_URL (e.g. https://your-app.vercel.app) in Render/Railway
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5175",
    "http://localhost:5176",
    "http://127.0.0.1:5176",
]
frontend_url = os.getenv("FRONTEND_URL", "").rstrip("/")
if frontend_url:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# ✅ request + response schemas
class ChatRequest(BaseModel):
    query: Optional[str] = None
    message: Optional[str] = None  # Frontend sends "message" instead of "query"
    session_id: Optional[str] = None  # Frontend sends session_id (not used yet but accepted)

class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = []
    citations: Optional[list[str]] = None  # Frontend also looks for "citations"

# ✅ Health check endpoint
@app.get("/")
def root():
    return {"status": "ok", "message": "Backend is running"}


# ✅ Explicit OPTIONS handlers so CORS preflight always succeeds (avoids 400)
@app.options("/api/sessions")
@app.options("/api/chat")
@app.options("/api/sessions/{session_id}")
def options_handler():
    return {}

# ✅ chat endpoint - matches frontend expectation of /api/chat
@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        # Handle both "query" and "message" field names
        query = req.query or req.message
        if not query:
            return {
                "answer": "Error: No query or message provided",
                "sources": [],
                "citations": []
            }
        
        # Invoke the LangGraph agent
        result = agent.invoke({"query": query})

        return {
            "answer": result.get("answer", "No answer generated"),
            "sources": result.get("sources", []),
            "citations": result.get("sources", []),  # Also provide as citations for frontend compatibility
        }
    except Exception as e:
        # Log the error and return a proper response (so CORS headers are sent)
        import traceback
        print(f"Error in chat endpoint: {e}")
        print(traceback.format_exc())
        return {
            "answer": f"Error processing request: {str(e)}",
            "sources": [],
            "citations": []
        }

# ✅ Also keep /chat endpoint for backward compatibility
@app.post("/chat", response_model=ChatResponse)
def chat_legacy(req: ChatRequest):
    query = req.query or req.message
    if not query:
        return {
            "answer": "Error: No query or message provided",
            "sources": [],
            "citations": []
        }
    
    result = agent.invoke({"query": query})

    return {
        "answer": result.get("answer", "No answer generated"),
        "sources": result.get("sources", []),
        "citations": result.get("sources", []),
    }

# ✅ Session endpoint (simple implementation for frontend compatibility)
@app.post("/api/sessions")
def create_session():
    """Create a new session ID for the frontend"""
    import uuid
    return {"session_id": str(uuid.uuid4())}

@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: str):
    """Delete a session (placeholder - no actual session management yet)"""
    return {"message": "Session deleted", "session_id": session_id}
