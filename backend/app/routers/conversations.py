from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_db
from app.db import crud
from app.db.models import ConversationRow, MessageRow
from app.models.schemas import (
    Conversation,
    Message,
    CreateConversationRequest,
    UpdateConversationRequest,
)

router = APIRouter(prefix="/api/conversations")


def _conv_to_schema(row: ConversationRow) -> Conversation:
    return Conversation(
        id=str(row.id),
        title=row.title,
        createdAt=row.created_at.isoformat(),
        updatedAt=row.updated_at.isoformat(),
    )


def _msg_to_schema(row: MessageRow) -> Message:
    return Message(
        id=str(row.id),
        role=row.role,
        content=row.content,
        toolResults=row.tool_results,
        timestamp=row.created_at.isoformat(),
    )


def _parse_uuid(conv_id: str) -> UUID:
    try:
        return UUID(conv_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid conversation ID format")


@router.get("")
async def list_conversations(
    db: AsyncSession = Depends(get_db),
) -> list[Conversation]:
    rows = await crud.list_conversations(db)
    return [_conv_to_schema(r) for r in rows]


@router.post("")
async def create_conversation(
    body: CreateConversationRequest = CreateConversationRequest(),
    db: AsyncSession = Depends(get_db),
) -> Conversation:
    row = await crud.create_conversation(db, title=body.title or "New conversation")
    return _conv_to_schema(row)


@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
) -> Conversation:
    uid = _parse_uuid(conversation_id)
    row = await crud.get_conversation(db, uid)
    if row is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return _conv_to_schema(row)


@router.patch("/{conversation_id}")
async def update_conversation(
    conversation_id: str,
    body: UpdateConversationRequest,
    db: AsyncSession = Depends(get_db),
) -> Conversation:
    uid = _parse_uuid(conversation_id)
    row = await crud.update_conversation(db, uid, body.title)
    if row is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return _conv_to_schema(row)


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
):
    uid = _parse_uuid(conversation_id)
    deleted = await crud.delete_conversation(db, uid)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"ok": True}


@router.get("/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[Message]:
    uid = _parse_uuid(conversation_id)
    conv = await crud.get_conversation(db, uid)
    if conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    rows = await crud.get_messages(db, uid)
    return [_msg_to_schema(r) for r in rows]
