"""
Recommendation Engine Agent - Provides personalized travel recommendations.
"""
import logging
from typing import Dict, Any, List

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from src.graphs.state.conversation_state import ConversationState
from src.tools.external_apis.flights_tool import FlightsTool
from src.tools.external_apis.hotels_tool import HotelsTool
from src.tools.external_apis.activities_tool import ActivitiesTool

logger = logging.getLogger(__name__)


class RecommenderAgent:
    """
    Specialized agent for generating travel recommendations.
    
    Provides recommendations for:
    - Flights
    - Hotels
    - Activities
    - Restaurants
    - Transportation
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm = ChatOpenAI(
            model=config.get("model_name", "gpt-4-turbo-preview"),
            temperature=config.get("temperature", 0.7)
        )
        
        # Initialize tools
        self.tools = [
            FlightsTool(),
            HotelsTool(),
            ActivitiesTool(),
        ]
        
        # Create agent
        self.agent = self._create_agent()
        
        logger.info("Recommender Agent initialized")
    
    def _create_agent(self) -> AgentExecutor:
        """Create the recommendation agent with tools."""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert travel recommendation specialist.
            
            Your role is to provide personalized recommendations for:
            - Flights: Best routes, airlines, and times based on budget and preferences
            - Accommodations: Hotels, hostels, vacation rentals matching style and budget
            - Activities: Tours, experiences, and attractions aligned with interests
            - Dining: Restaurants and food experiences
            - Transportation: Local transport options
            
            Use the available tools to search for and compare options.
            
            Consider:
            - User budget constraints
            - Travel style and preferences
            - Location and accessibility
            - Reviews and ratings
            - Value for money
            
            Provide 3-5 options for each category with:
            - Clear descriptions
            - Pricing information
            - Pros and cons
            - Booking links or contact information
            """),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_functions_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True)
    
    async def get_recommendations(
        self,
        state: ConversationState
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate comprehensive travel recommendations.
        
        Args:
            state: Current conversation state
        
        Returns:
            Dictionary with recommendations by category
        """
        logger.info("Generating travel recommendations")
        
        trip_details = state["trip_details"]
        preferences = state["user_preferences"]
        
        # Prepare input for the agent
        input_text = self._format_recommender_input(trip_details, preferences)
        
        # Run the agent
        result = await self.agent.ainvoke({"input": input_text})
        
        # Parse recommendations
        recommendations = self._parse_recommendations(result["output"])
        
        logger.info(f"Generated recommendations for {len(recommendations)} categories")
        return recommendations
    
    async def get_flight_recommendations(
        self,
        state: ConversationState
    ) -> List[Dict[str, Any]]:
        """Get specific flight recommendations."""
        logger.info("Getting flight recommendations")
        
        trip_details = state["trip_details"]
        
        input_text = f"""Find the best flight options for:
        
Origin: {trip_details.get('origin', 'User location')}
Destination: {trip_details.get('destination')}
Departure Date: {trip_details.get('start_date')}
Return Date: {trip_details.get('end_date')}
Passengers: {trip_details.get('num_travelers', 1)}
Budget: {state['user_preferences'].get('budget', 'moderate')}

Provide 3-5 flight options with pricing, airlines, and schedules.
"""
        
        result = await self.agent.ainvoke({"input": input_text})
        return self._parse_flight_recommendations(result["output"])
    
    async def get_hotel_recommendations(
        self,
        state: ConversationState
    ) -> List[Dict[str, Any]]:
        """Get specific hotel recommendations."""
        logger.info("Getting hotel recommendations")
        
        trip_details = state["trip_details"]
        preferences = state["user_preferences"]
        
        input_text = f"""Find the best accommodation options for:
        
Destination: {trip_details.get('destination')}
Check-in: {trip_details.get('start_date')}
Check-out: {trip_details.get('end_date')}
Guests: {trip_details.get('num_travelers', 1)}
Type: {preferences.get('accommodation_type', 'hotel')}
Budget: {preferences.get('budget', 'moderate')}
Location Preference: {preferences.get('location_preference', 'city center')}

Provide 3-5 accommodation options with amenities, pricing, and locations.
"""
        
        result = await self.agent.ainvoke({"input": input_text})
        return self._parse_hotel_recommendations(result["output"])
    
    async def get_activity_recommendations(
        self,
        state: ConversationState,
        specific_interests: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Get specific activity recommendations."""
        logger.info("Getting activity recommendations")
        
        trip_details = state["trip_details"]
        preferences = state["user_preferences"]
        
        interests = specific_interests or preferences.get('interests', [])
        
        input_text = f"""Find the best activities and experiences for:
        
Destination: {trip_details.get('destination')}
Duration: {trip_details.get('duration_days')} days
Interests: {', '.join(interests)}
Travel Style: {preferences.get('travel_style', 'balanced')}
Budget: {preferences.get('budget', 'moderate')}

Provide diverse activity recommendations including:
- Must-see attractions
- Unique experiences
- Local activities
- Day trips
"""
        
        result = await self.agent.ainvoke({"input": input_text})
        return self._parse_activity_recommendations(result["output"])
    
    def _format_recommender_input(
        self,
        trip_details: Dict[str, Any],
        preferences: Dict[str, Any]
    ) -> str:
        """Format input for the recommender agent."""
        
        return f"""Generate comprehensive travel recommendations for:

Trip Details:
- Destination: {trip_details.get('destination')}
- Dates: {trip_details.get('start_date')} to {trip_details.get('end_date')}
- Duration: {trip_details.get('duration_days')} days
- Travelers: {trip_details.get('num_travelers', 1)}

Preferences:
- Budget: {preferences.get('budget', 'moderate')}
- Travel Style: {preferences.get('travel_style', 'balanced')}
- Interests: {', '.join(preferences.get('interests', []))}
- Accommodation Type: {preferences.get('accommodation_type', 'hotel')}

Please provide recommendations for flights, hotels, and activities.
"""
    
    def _parse_recommendations(self, agent_output: str) -> Dict[str, List[Dict[str, Any]]]:
        """Parse agent output into structured recommendations."""
        # TODO: Implement sophisticated parsing
        # For now, return placeholder structure
        return {
            "flights": [],
            "hotels": [],
            "activities": [],
            "restaurants": [],
            "transportation": []
        }
    
    def _parse_flight_recommendations(self, output: str) -> List[Dict[str, Any]]:
        """Parse flight recommendations from agent output."""
        # TODO: Implement parsing
        return []
    
    def _parse_hotel_recommendations(self, output: str) -> List[Dict[str, Any]]:
        """Parse hotel recommendations from agent output."""
        # TODO: Implement parsing
        return []
    
    def _parse_activity_recommendations(self, output: str) -> List[Dict[str, Any]]:
        """Parse activity recommendations from agent output."""
        # TODO: Implement parsing
        return []
