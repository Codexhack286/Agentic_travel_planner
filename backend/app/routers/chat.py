import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_db
from app.db import crud
from app.models.schemas import ChatRequest
from app.services.mock_agent import generate_mock_response

router = APIRouter()


def _parse_uuid(conv_id: str) -> UUID:
    try:
        return UUID(conv_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid conversation ID format")


@router.post("/api/chat")
async def chat(
    body: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    uid = _parse_uuid(body.conversation_id)

    # Verify conversation exists
    conv = await crud.get_conversation(db, uid)
    if conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Store the user message
    await crud.add_message(db, uid, role="user", content=body.message)
    await db.commit()

    async def event_stream():
        full_content = ""
        tool_results = []

        async for chunk in generate_mock_response(body.message):
            yield chunk

            # Parse the SSE chunk to capture content for storage
            for line in chunk.strip().split("\n"):
                if not line.startswith("data: "):
                    continue
                raw = line[6:].strip()
                if raw == "[DONE]":
                    continue
                try:
                    event = json.loads(raw)
                    if event["type"] == "token":
                        full_content += event["content"]
                    elif event["type"] == "tool_result":
                        tool_results.append(event["content"])
                except (json.JSONDecodeError, KeyError):
                    pass

        # Store assistant message after streaming completes
        from app.db.engine import async_session

        async with async_session() as session:
            await crud.add_message(
                session,
                uid,
                role="assistant",
                content=full_content.strip(),
                tool_results=tool_results if tool_results else None,
            )
            await session.commit()

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
