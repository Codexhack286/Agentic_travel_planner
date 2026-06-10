import asyncio
import json
import os
import sys
from typing import AsyncGenerator
from uuid import UUID

# Add ai-travel-concierge root to python path dynamically
AGENT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../ai-travel-concierge"))
sys.path.insert(0, AGENT_ROOT)

from src.graphs.workflows.travel_concierge_graph import TravelConciergeGraph
from src.graphs.state.conversation_state import create_initial_state
from app.db import crud
from app.db.engine import async_session

# We can initialize it lazily or globally
_travel_graph_instance = None

def get_travel_graph() -> TravelConciergeGraph:
    global _travel_graph_instance
    if _travel_graph_instance is None:
        # Avoid loading everything at module load if not needed
        from src.utils.config import load_config
        config = load_config()
        _travel_graph_instance = TravelConciergeGraph(config)
    return _travel_graph_instance

async def generate_real_response(message: str, conversation_id: str) -> AsyncGenerator[str, None]:
    """Stream response from the real LangGraph as SSE events."""
    graph = get_travel_graph()
    
    # 1. Load conversation messages from DB
    async with async_session() as session:
        db_messages = await crud.get_messages(session, UUID(conversation_id))
        
    db_msg_list = [{"role": msg.role, "content": msg.content} for msg in db_messages]
    
    config = {"configurable": {"thread_id": conversation_id}}
    
    try:
        # 2. Check existing checkpoint state
        checkpoint_state = await graph.graph.aget_state(config)
        checkpoint_messages = checkpoint_state.values.get("messages", []) if checkpoint_state.values else []
        
        # 3. Determine if we need to sync history or just pass new messages
        if not checkpoint_messages:
            # Checkpoint is empty (e.g. server restart or first message)
            state = create_initial_state(user_id=conversation_id)
            state["messages"] = db_msg_list
            result_state = await graph.graph.ainvoke(state, config)
        else:
            # Checkpoint exists, determine suffix not yet in checkpoint
            num_existing = len(checkpoint_messages)
            new_messages = db_msg_list[num_existing:]
            if new_messages:
                result_state = await graph.graph.ainvoke({"messages": new_messages}, config)
            else:
                result_state = checkpoint_state.values
                
        # 4. Extract assistant response
        assistant_messages = [
            msg["content"] for msg in result_state["messages"] 
            if msg["role"] == "assistant"
        ]
        text_response = assistant_messages[-1] if assistant_messages else "I'm sorry, I couldn't process that request."
        
        # 5. Extract current tool result
        current_tool_result = result_state.get("current_tool_result")
        
        # 6. Stream tool_result event first if present
        if current_tool_result:
            tool_event = json.dumps({"type": "tool_result", "content": current_tool_result})
            yield f"data: {tool_event}\n\n"
            await asyncio.sleep(0.1)
            
        # 7. Stream text tokens
        words = text_response.split(" ")
        for word in words:
            token = word + " "
            event = json.dumps({"type": "token", "content": token})
            yield f"data: {event}\n\n"
            await asyncio.sleep(0.04)
            
        # 8. Complete event
        complete_content = {
            "role": "assistant",
            "content": text_response
        }
        if current_tool_result:
            complete_content["toolResults"] = [current_tool_result]
            
        event = json.dumps({"type": "complete", "content": complete_content})
        yield f"data: {event}\n\n"
        yield "data: [DONE]\n\n"

    except Exception as e:
        error_msg = f"Sorry, I encountered an error: {e}"
        event = json.dumps({"type": "token", "content": error_msg})
        yield f"data: {event}\n\n"
        
        complete_content = {
            "role": "assistant",
            "content": error_msg
        }
        event = json.dumps({"type": "complete", "content": complete_content})
        yield f"data: {event}\n\n"
        yield "data: [DONE]\n\n"
