"""
State definitions for the Travel Concierge graph.
"""
from typing import TypedDict, List, Optional, Dict, Any, Annotated
from datetime import datetime
import operator


class TravelPreferences(TypedDict):
    """User travel preferences."""
    budget: Optional[str]
    travel_style: Optional[str]  # adventure, luxury, budget, cultural, etc.
    accommodation_type: Optional[str]
    interests: List[str]
    dietary_restrictions: List[str]
    accessibility_needs: List[str]


class TripDetails(TypedDict):
    """Trip planning details."""
    destination: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    duration_days: Optional[int]
    num_travelers: int
    purpose: Optional[str]  # business, leisure, family, etc.


class Itinerary(TypedDict):
    """Itinerary structure."""
    day: int
    date: datetime
    activities: List[Dict[str, Any]]
    meals: List[Dict[str, Any]]
    accommodation: Optional[Dict[str, Any]]
    notes: Optional[str]


class ConversationState(TypedDict):
    """
    Main state for the Travel Concierge conversation graph.
    
    This state is passed between nodes in the LangGraph workflow.
    """
    # Conversation tracking
    messages: Annotated[List[Dict[str, str]], operator.add]
    current_intent: Optional[str]
    conversation_id: str
    
    # User information
    user_id: Optional[str]
    user_preferences: TravelPreferences
    
    # Trip planning
    trip_details: TripDetails
    itinerary: List[Itinerary]
    
    # Recommendations
    recommendations: Dict[str, List[Dict[str, Any]]]  # flights, hotels, activities, etc.
    
    # Booking information
    bookings: List[Dict[str, Any]]
    
    # RAG context
    retrieved_context: List[str]
    
    # Agent metadata
    current_agent: Optional[str]
    next_action: Optional[str]
    
    # Error handling
    error: Optional[str]
    retry_count: int
    
    # Flags
    needs_more_info: bool
    ready_to_book: bool
    conversation_complete: bool


def create_initial_state(user_id: Optional[str] = None) -> ConversationState:
    """Create an initial conversation state."""
    return ConversationState(
        messages=[],
        current_intent=None,
        conversation_id=f"conv_{datetime.now().timestamp()}",
        user_id=user_id,
        user_preferences=TravelPreferences(
            budget=None,
            travel_style=None,
            accommodation_type=None,
            interests=[],
            dietary_restrictions=[],
            accessibility_needs=[]
        ),
        trip_details=TripDetails(
            destination=None,
            start_date=None,
            end_date=None,
            duration_days=None,
            num_travelers=1,
            purpose=None
        ),
        itinerary=[],
        recommendations={},
        bookings=[],
        retrieved_context=[],
        current_agent=None,
        next_action=None,
        error=None,
        retry_count=0,
        needs_more_info=False,
        ready_to_book=False,
        conversation_complete=False
    )
