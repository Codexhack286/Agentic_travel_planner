from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ConversationRow, MessageRow


async def list_conversations(db: AsyncSession) -> list[ConversationRow]:
    result = await db.execute(
        select(ConversationRow).order_by(ConversationRow.updated_at.desc())
    )
    return list(result.scalars().all())


async def get_conversation(
    db: AsyncSession, conv_id: UUID
) -> ConversationRow | None:
    return await db.get(ConversationRow, conv_id)


async def create_conversation(
    db: AsyncSession, title: str = "New conversation"
) -> ConversationRow:
    conv = ConversationRow(title=title)
    db.add(conv)
    await db.flush()
    return conv


async def update_conversation(
    db: AsyncSession, conv_id: UUID, title: str
) -> ConversationRow | None:
    conv = await db.get(ConversationRow, conv_id)
    if conv is None:
        return None
    conv.title = title
    conv.updated_at = datetime.now(timezone.utc)
    await db.flush()
    return conv


async def delete_conversation(db: AsyncSession, conv_id: UUID) -> bool:
    conv = await db.get(ConversationRow, conv_id)
    if conv is None:
        return False
    await db.delete(conv)
    await db.flush()
    return True


async def get_messages(
    db: AsyncSession, conv_id: UUID
) -> list[MessageRow]:
    result = await db.execute(
        select(MessageRow)
        .where(MessageRow.conversation_id == conv_id)
        .order_by(MessageRow.created_at.asc())
    )
    return list(result.scalars().all())


async def add_message(
    db: AsyncSession,
    conv_id: UUID,
    role: str,
    content: str,
    tool_results: list | None = None,
) -> MessageRow:
    msg = MessageRow(
        conversation_id=conv_id,
        role=role,
        content=content,
        tool_results=tool_results,
    )
    db.add(msg)

    # Update conversation's updated_at
    conv = await db.get(ConversationRow, conv_id)
    if conv:
        conv.updated_at = datetime.now(timezone.utc)

    await db.flush()
    return msg
