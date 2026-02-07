"""
Edge routing logic for the Travel Concierge LangGraph workflow.
"""
from typing import Literal
import logging

from src.graphs.state.conversation_state import ConversationState

logger = logging.getLogger(__name__)


class GraphEdges:
    """Collection of edge routing functions for the travel concierge graph."""
    
    @staticmethod
    def route_by_intent(
        state: ConversationState
    ) -> Literal["plan_trip", "recommend", "book", "answer_question", "clarify"]:
        """
        Route to the appropriate node based on classified intent.
        
        Returns the name of the next node to execute.
        """
        intent = state.get("current_intent")
        
        logger.info(f"Routing based on intent: {intent}")
        
        # Check if we need more information first
        if state.get("needs_more_info"):
            return "clarify"
        
        # Route based on intent
        if intent == "plan_trip":
            return "plan_trip"
        elif intent == "get_recommendations":
            return "recommend"
        elif intent == "book_travel":
            return "book"
        elif intent == "ask_question":
            return "answer_question"
        elif intent == "modify_itinerary":
            return "plan_trip"  # Re-run planner with modifications
        else:
            # Default to answering questions
            return "answer_question"
    
    @staticmethod
    def should_continue(
        state: ConversationState
    ) -> Literal["continue", "end"]:
        """
        Determine if the conversation should continue or end.
        
        Returns:
            "continue" if more interaction is needed
            "end" if the conversation is complete
        """
        logger.info("Checking if conversation should continue")
        
        # End conversation if explicitly marked as complete
        if state.get("conversation_complete"):
            logger.info("Conversation marked as complete")
            return "end"
        
        # End if there's an unrecoverable error
        if state.get("error") and state.get("retry_count", 0) >= 3:
            logger.warning("Max retries reached, ending conversation")
            return "end"
        
        # Continue if waiting for more information
        if state.get("needs_more_info"):
            logger.info("Waiting for more information, continuing")
            return "continue"
        
        # Default to continue
        return "continue"
    
    @staticmethod
    def check_information_complete(
        state: ConversationState
    ) -> Literal["retrieve_context", "clarify"]:
        """
        Check if we have enough information to proceed.
        
        Returns:
            "retrieve_context" if we have enough info
            "clarify" if we need more information
        """
        trip_details = state.get("trip_details", {})
        
        # Check required fields based on intent
        intent = state.get("current_intent")
        
        if intent == "plan_trip":
            required_fields = ["destination", "start_date", "duration_days"]
            missing = [f for f in required_fields if not trip_details.get(f)]
            
            if missing:
                logger.info(f"Missing required fields for planning: {missing}")
                return "clarify"
        
        elif intent == "book_travel":
            if not state.get("itinerary") and not state.get("recommendations"):
                logger.info("No itinerary or recommendations to book")
                return "clarify"
        
        # Sufficient information available
        logger.info("Sufficient information available, proceeding to retrieve context")
        return "retrieve_context"
    
    @staticmethod
    def route_after_clarification(
        state: ConversationState
    ) -> Literal["classify_intent", "end"]:
        """
        Route after receiving clarification from user.
        
        Returns:
            "classify_intent" to re-process with new information
            "end" if user wants to exit
        """
        latest_message = state["messages"][-1]["content"].lower()
        
        # Check for exit intent
        exit_phrases = ["exit", "quit", "bye", "no thanks", "cancel"]
        if any(phrase in latest_message for phrase in exit_phrases):
            logger.info("User wants to exit")
            return "end"
        
        # Re-classify intent with new information
        logger.info("Re-classifying intent after clarification")
        return "classify_intent"
    
    @staticmethod
    def handle_error(
        state: ConversationState
    ) -> Literal["retry", "end"]:
        """
        Determine whether to retry after an error or end the conversation.
        
        Returns:
            "retry" if we should retry the current operation
            "end" if we should give up
        """
        retry_count = state.get("retry_count", 0)
        max_retries = 3
        
        if retry_count < max_retries:
            logger.info(f"Retrying operation (attempt {retry_count + 1}/{max_retries})")
            return "retry"
        else:
            logger.error("Max retries exceeded, ending conversation")
            return "end"
