from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.db import get_db
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage, MessageRole
from app.schemas.chat import SessionCreate, SessionOut, MessageCreate, MessageOut, ChatResponse
from app.auth.dependencies import get_current_user
from app.agents.memory_agent import MemoryAgent
from app.services.vector_memory_service import store_memory
from app.ai.llm import ask_llm
from datetime import datetime

router = APIRouter(prefix="/chat", tags=["Chat"])

SYSTEM_HINT = """You are a personal AI mentor with deep knowledge of the user's goals,
projects, tasks, and long-term memory. Be specific, warm, and actionable.
Reference the user's actual data when relevant."""


@router.post("/sessions", response_model=SessionOut, status_code=201)
def create_session(
    payload: SessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = ChatSession(user_id=current_user.id, title=payload.title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/sessions", response_model=List[SessionOut])
def list_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).order_by(ChatSession.updated_at.desc()).all()


@router.get("/sessions/{session_id}/messages", response_model=List[MessageOut])
def get_messages(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return session.messages


@router.post("/sessions/{session_id}/messages", response_model=ChatResponse, status_code=201)
def send_message(
    session_id: int,
    payload: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    # Save user message
    user_msg = ChatMessage(
        session_id=session_id,
        role=MessageRole.user,
        content=payload.content
    )
    db.add(user_msg)
    db.flush()

    # Build enriched context (structured + vector memories)
    agent = MemoryAgent(db, current_user.id)
    context = agent.build_full_context(query=payload.content)

    # Load last 10 messages for conversation continuity
    history = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at.desc()).limit(10).all()
    history_text = "\n".join(
        f"{m.role.value.upper()}: {m.content}"
        for m in reversed(history)
        if m.id != user_msg.id
    )

    prompt = f"""
{context}

## Conversation History
{history_text}

## Current Message
USER: {payload.content}

Respond as their personal AI mentor. Be specific and helpful.
"""

    ai_response = ask_llm(prompt, SYSTEM_HINT)

    # Save AI response
    assistant_msg = ChatMessage(
        session_id=session_id,
        role=MessageRole.assistant,
        content=ai_response
    )
    db.add(assistant_msg)

    # Update session timestamp
    session.updated_at = datetime.utcnow()

    # Store user message in vector memory
    store_memory(db, current_user.id, payload.content, tags="chat")

    # Auto-title session from first message
    if len(session.messages) <= 2:
        session.title = payload.content[:60] + ("..." if len(payload.content) > 60 else "")

    db.commit()
    db.refresh(user_msg)
    db.refresh(assistant_msg)

    return ChatResponse(user_message=user_msg, assistant_message=assistant_msg)
