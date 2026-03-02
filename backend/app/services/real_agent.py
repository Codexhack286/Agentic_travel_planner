import asyncio
import json
import os
import sys
from typing import AsyncGenerator

# Add ai-travel-concierge root to python path dynamically
AGENT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../ai-travel-concierge"))
sys.path.insert(0, AGENT_ROOT)

from src.graphs.workflows.travel_concierge_graph import TravelConciergeGraph
from src.graphs.state.conversation_state import create_initial_state

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
    
    # We will use the ainvoke method to run the state manually to get full state visibility
    state = create_initial_state(user_id=conversation_id)
    # Usually you'd load the state from your DB here if persisting conversation history.
    state["messages"].append({"role": "user", "content": message})
    
    config = {"configurable": {"thread_id": conversation_id}}
    
    try:
        # Run graph
        result_state = await graph.graph.ainvoke(state, config)
        
        # Look for the last assistant message
        assistant_messages = [
            msg["content"] for msg in result_state["messages"] 
            if msg["role"] == "assistant"
        ]
        text_response = assistant_messages[-1] if assistant_messages else "I'm sorry, I couldn't process that request."
        
        # Guess tool intent to map back to UI widgets just based on intent 
        # (Alternatively you can inspect result_state tool_calls/results)
        intent = result_state.get("current_intent", "default")
        
        # We can extract the raw API data and embed it in a tooltip / widget format if needed.
        # But for minimal changes, we just stream back text! (The mock agent sent mock tool_results).
        # Without tool_results, the UI will just display the text - which is perfectly compatible!

        # Stream text out
        words = text_response.split(" ")
        for word in words:
            token = word + " "
            event = json.dumps({"type": "token", "content": token})
            yield f"data: {event}\n\n"
            await asyncio.sleep(0.04)
        
        # Complete
        complete_content = {
            "role": "assistant",
            "content": text_response
        }
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
