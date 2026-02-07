"""
Node functions for the Travel Concierge LangGraph workflow.
"""
from typing import Dict, Any
import logging

from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

from src.graphs.state.conversation_state import ConversationState
from src.agents.travel_planner.planner_agent import TravelPlannerAgent
from src.agents.recommendation_engine.recommender_agent import RecommenderAgent
from src.agents.booking_assistant.booking_agent import BookingAgent
from src.retrievers.rag.travel_retriever import TravelRetriever

logger = logging.getLogger(__name__)


class GraphNodes:
    """Collection of node functions for the travel concierge graph."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm = ChatOpenAI(
            model=config.get("model_name", "gpt-4-turbo-preview"),
            temperature=config.get("temperature", 0.7)
        )
        self.travel_planner = TravelPlannerAgent(config)
        self.recommender = RecommenderAgent(config)
        self.booking_agent = BookingAgent(config)
        self.retriever = TravelRetriever(config)
    
    async def classify_intent_node(self, state: ConversationState) -> ConversationState:
        """
        Classify user intent from the latest message.
        
        Possible intents:
        - plan_trip: User wants to plan a new trip
        - get_recommendations: User wants recommendations
        - book_travel: User wants to make bookings
        - modify_itinerary: User wants to change plans
        - ask_question: User has a general travel question
        """
        logger.info("Node: Classifying user intent")
        
        latest_message = state["messages"][-1]["content"]
        
        prompt = f"""Classify the following user message into one of these intents:
        - plan_trip
        - get_recommendations
        - book_travel
        - modify_itinerary
        - ask_question
        
        User message: {latest_message}
        
        Respond with only the intent name."""
        
        response = await self.llm.ainvoke(prompt)
        intent = response.content.strip().lower()
        
        state["current_intent"] = intent
        logger.info(f"Classified intent: {intent}")
        
        return state
    
    async def retrieve_context_node(self, state: ConversationState) -> ConversationState:
        """Retrieve relevant context from vector store."""
        logger.info("Node: Retrieving context from RAG")
        
        latest_message = state["messages"][-1]["content"]
        
        # Retrieve relevant documents
        context_docs = await self.retriever.retrieve(
            query=latest_message,
            filters={
                "destination": state["trip_details"].get("destination"),
                "interests": state["user_preferences"].get("interests", [])
            }
        )
        
        state["retrieved_context"] = [doc.page_content for doc in context_docs]
        logger.info(f"Retrieved {len(context_docs)} context documents")
        
        return state
    
    async def plan_trip_node(self, state: ConversationState) -> ConversationState:
        """Generate travel itinerary using the Travel Planner agent."""
        logger.info("Node: Planning trip")
        
        state["current_agent"] = "travel_planner"
        
        # Generate itinerary
        itinerary = await self.travel_planner.create_itinerary(state)
        
        state["itinerary"] = itinerary
        state["needs_more_info"] = False
        
        # Add response to messages
        response_message = self._format_itinerary_response(itinerary)
        state["messages"].append({
            "role": "assistant",
            "content": response_message
        })
        
        return state
    
    async def recommend_node(self, state: ConversationState) -> ConversationState:
        """Generate recommendations using the Recommender agent."""
        logger.info("Node: Generating recommendations")
        
        state["current_agent"] = "recommender"
        
        # Get recommendations
        recommendations = await self.recommender.get_recommendations(state)
        
        state["recommendations"] = recommendations
        
        # Add response to messages
        response_message = self._format_recommendations_response(recommendations)
        state["messages"].append({
            "role": "assistant",
            "content": response_message
        })
        
        return state
    
    async def booking_node(self, state: ConversationState) -> ConversationState:
        """Handle booking requests using the Booking agent."""
        logger.info("Node: Processing booking request")
        
        state["current_agent"] = "booking_agent"
        
        # Process booking
        booking_result = await self.booking_agent.process_booking(state)
        
        state["bookings"].append(booking_result)
        
        # Add response to messages
        response_message = self._format_booking_response(booking_result)
        state["messages"].append({
            "role": "assistant",
            "content": response_message
        })
        
        return state
    
    async def clarification_node(self, state: ConversationState) -> ConversationState:
        """Ask for clarification when information is missing."""
        logger.info("Node: Requesting clarification")
        
        missing_info = self._identify_missing_info(state)
        
        clarification_message = (
            f"To help you better, I need some additional information: {missing_info}"
        )
        
        state["messages"].append({
            "role": "assistant",
            "content": clarification_message
        })
        state["needs_more_info"] = True
        
        return state
    
    async def answer_question_node(self, state: ConversationState) -> ConversationState:
        """Answer general travel questions using RAG."""
        logger.info("Node: Answering travel question")
        
        latest_message = state["messages"][-1]["content"]
        context = "\n".join(state["retrieved_context"])
        
        prompt = f"""Answer the following travel question using the provided context.
        
        Context:
        {context}
        
        Question: {latest_message}
        
        Provide a helpful and accurate answer."""
        
        response = await self.llm.ainvoke(prompt)
        
        state["messages"].append({
            "role": "assistant",
            "content": response.content
        })
        
        return state
    
    def _format_itinerary_response(self, itinerary: list) -> str:
        """Format itinerary into a readable response."""
        # Implementation here
        return "Here's your personalized itinerary..."
    
    def _format_recommendations_response(self, recommendations: dict) -> str:
        """Format recommendations into a readable response."""
        # Implementation here
        return "Here are my recommendations..."
    
    def _format_booking_response(self, booking_result: dict) -> str:
        """Format booking result into a readable response."""
        # Implementation here
        return "Your booking has been processed..."
    
    def _identify_missing_info(self, state: ConversationState) -> str:
        """Identify what information is missing from the state."""
        missing = []
        
        if not state["trip_details"].get("destination"):
            missing.append("destination")
        if not state["trip_details"].get("start_date"):
            missing.append("travel dates")
        if not state["user_preferences"].get("budget"):
            missing.append("budget")
        
        return ", ".join(missing)
