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


class DocumentSource(BaseModel):
    document_id: str
    document_name: str


class MessageOut(BaseModel):
    id: str
    thread_id: str
    role: str
    content: str
    sources: Optional[list[DocumentSource]] = None
    created_at: datetime


class DocumentOut(BaseModel):
    id: str
    name: str
    file_type: str
    source: str
    status: str
    error_message: Optional[str] = None
    chunk_count: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class DriveConnectionOut(BaseModel):
    connected: bool
    folder_id: Optional[str] = None
    folder_name: Optional[str] = None
    last_synced_at: Optional[datetime] = None


class DriveFolderItem(BaseModel):
    id: str
    name: str
