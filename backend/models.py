from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ChatRequest(BaseModel):
    thread_id: Optional[str] = None
    message: str


class ThreadCreate(BaseModel):
    title: str = "New Thread"


class ThreadOut(BaseModel):
    id: str
    openai_thread_id: Optional[str] = None
    title: str
    created_at: datetime
    updated_at: datetime


class MessageOut(BaseModel):
    id: str
    thread_id: str
    role: str
    content: str
    created_at: datetime
