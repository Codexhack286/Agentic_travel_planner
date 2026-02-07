"""
Main Travel Concierge LangGraph workflow definition.
"""
import logging
from typing import Dict, Any

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from src.graphs.state.conversation_state import ConversationState, create_initial_state
from src.graphs.nodes.graph_nodes import GraphNodes
from src.graphs.edges.graph_edges import GraphEdges

logger = logging.getLogger(__name__)


class TravelConciergeGraph:
    """
    Main LangGraph workflow for the AI Travel Concierge.
    
    This graph orchestrates the conversation flow between different
    specialized agents and handles state management.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the travel concierge graph.
        
        Args:
            config: Configuration dictionary with model settings, API keys, etc.
        """
        self.config = config
        self.nodes = GraphNodes(config)
        self.edges = GraphEdges()
        self.graph = self._build_graph()
        
        logger.info("Travel Concierge Graph initialized")
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow.
        
        Returns:
            Compiled StateGraph ready for execution
        """
        # Create the graph
        workflow = StateGraph(ConversationState)
        
        # Add nodes
        workflow.add_node("classify_intent", self.nodes.classify_intent_node)
        workflow.add_node("check_info", self._check_info_node)
        workflow.add_node("retrieve_context", self.nodes.retrieve_context_node)
        workflow.add_node("plan_trip", self.nodes.plan_trip_node)
        workflow.add_node("recommend", self.nodes.recommend_node)
        workflow.add_node("book", self.nodes.booking_node)
        workflow.add_node("answer_question", self.nodes.answer_question_node)
        workflow.add_node("clarify", self.nodes.clarification_node)
        
        # Set entry point
        workflow.set_entry_point("classify_intent")
        
        # Add edges
        # After classifying intent, check if we have enough information
        workflow.add_edge("classify_intent", "check_info")
        
        # From check_info, either retrieve context or ask for clarification
        workflow.add_conditional_edges(
            "check_info",
            self.edges.check_information_complete,
            {
                "retrieve_context": "retrieve_context",
                "clarify": "clarify"
            }
        )
        
        # After retrieving context, route based on intent
        workflow.add_conditional_edges(
            "retrieve_context",
            self.edges.route_by_intent,
            {
                "plan_trip": "plan_trip",
                "recommend": "recommend",
                "book": "book",
                "answer_question": "answer_question",
                "clarify": "clarify"
            }
        )
        
        # After each action node, check if we should continue
        for node in ["plan_trip", "recommend", "book", "answer_question"]:
            workflow.add_conditional_edges(
                node,
                self.edges.should_continue,
                {
                    "continue": END,  # Wait for next user input
                    "end": END
                }
            )
        
        # After clarification, re-classify intent or end
        workflow.add_conditional_edges(
            "clarify",
            self.edges.route_after_clarification,
            {
                "classify_intent": "classify_intent",
                "end": END
            }
        )
        
        # Compile the graph with memory
        memory = MemorySaver()
        compiled_graph = workflow.compile(checkpointer=memory)
        
        logger.info("Graph workflow compiled successfully")
        return compiled_graph
    
    def _check_info_node(self, state: ConversationState) -> ConversationState:
        """
        Wrapper node to maintain compatibility with edge routing.
        This node doesn't modify state, just acts as a routing point.
        """
        return state
    
    async def run(
        self,
        user_input: str,
        user_id: str = None,
        conversation_id: str = None
    ) -> str:
        """
        Run the travel concierge graph with user input.
        
        Args:
            user_input: The user's message
            user_id: Optional user identifier
            conversation_id: Optional conversation identifier for resuming
        
        Returns:
            The assistant's response
        """
        logger.info(f"Processing user input: {user_input[:50]}...")
        
        # Create or load state
        if conversation_id:
            # Load existing conversation state
            # This would integrate with your memory/database
            state = self._load_conversation(conversation_id)
        else:
            # Create new conversation state
            state = create_initial_state(user_id)
        
        # Add user message to state
        state["messages"].append({
            "role": "user",
            "content": user_input
        })
        
        # Run the graph
        config = {"configurable": {"thread_id": state["conversation_id"]}}
        
        try:
            result = await self.graph.ainvoke(state, config)
            
            # Extract assistant's response
            assistant_messages = [
                msg["content"] for msg in result["messages"]
                if msg["role"] == "assistant"
            ]
            
            response = assistant_messages[-1] if assistant_messages else "I'm sorry, I couldn't process that request."
            
            logger.info("Successfully processed user input")
            return response
            
        except Exception as e:
            logger.error(f"Error running graph: {e}", exc_info=True)
            return "I apologize, but I encountered an error. Please try again."
    
    def _load_conversation(self, conversation_id: str) -> ConversationState:
        """
        Load existing conversation state.
        
        This should integrate with your persistence layer.
        """
        # Placeholder - implement based on your storage solution
        logger.info(f"Loading conversation: {conversation_id}")
        return create_initial_state()
    
    def visualize(self, output_path: str = "travel_graph.png"):
        """
        Generate a visualization of the graph structure.
        
        Args:
            output_path: Path to save the visualization
        """
        try:
            from langchain_core.runnables.graph import MermaidDrawMethod
            
            graph_image = self.graph.get_graph().draw_mermaid_png(
                draw_method=MermaidDrawMethod.API
            )
            
            with open(output_path, "wb") as f:
                f.write(graph_image)
            
            logger.info(f"Graph visualization saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to generate visualization: {e}")
