from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ChatRequest(BaseModel):
    conversation_id: str
    message: str


class CreateConversationRequest(BaseModel):
    title: Optional[str] = None


class UpdateConversationRequest(BaseModel):
    title: str


class Conversation(BaseModel):
    id: str
    title: str
    createdAt: str
    updatedAt: str


class Message(BaseModel):
    id: Optional[str] = None
    role: str
    content: str
    toolResults: Optional[list] = None
    timestamp: str


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
    llm_provider: str = "mock"
