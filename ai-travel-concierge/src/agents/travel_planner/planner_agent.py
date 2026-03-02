"""
Travel Planner Agent - Creates personalized itineraries.
"""
import logging
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta

from langchain_groq import ChatGroq
from langchain_classic.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from src.graphs.state.conversation_state import ConversationState, Itinerary
from src.tools.external_apis import PlacesTool, WeatherTool

logger = logging.getLogger(__name__)


class TravelPlannerAgent:
    """
    Specialized agent for creating travel itineraries.
    
    This agent uses LangChain's function calling to access external tools
    and create detailed, personalized travel plans.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm = ChatGroq(
            model=config.get("model_name", "openai/gpt-oss-120b"),
            temperature=config.get("temperature", 0.7)
        )
        
        # Initialize tools
        self.tools = [
            PlacesTool(),
            WeatherTool(),
        ]
        
        # Create agent
        self.agent = self._create_agent()
        
        logger.info("Travel Planner Agent initialized")
    
    def _create_agent(self) -> AgentExecutor:
        """Create the travel planner agent with tools."""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert travel planner with deep knowledge of destinations worldwide.
            
            Your role is to create detailed, personalized itineraries based on:
            - User preferences (budget, travel style, interests)
            - Trip details (destination, dates, duration)
            - Retrieved context about the destination
            
            Use the available tools to:
            1. Find popular attractions and activities
            2. Check weather conditions
            3. Recommend restaurants and dining options
            4. Suggest accommodations
            
            Create day-by-day itineraries that are:
            - Realistic and achievable
            - Well-paced with breaks
            - Aligned with user preferences
            - Include timing, locations, and practical tips
            
            Format each day clearly with activities, meals, and notes.
            """),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True)
    
    async def create_itinerary(self, state: ConversationState) -> Tuple[List[Itinerary], str]:
        """
        Create a detailed travel itinerary based on state.
        
        Args:
            state: Current conversation state
        
        Returns:
            Tuple of (List of daily itinerary items, raw agent output string)
        """
        logger.info("Creating travel itinerary")
        
        trip_details = state["trip_details"]
        preferences = state["user_preferences"]
        context = state.get("retrieved_context", [])
        
        # Prepare input for the agent
        input_text = self._format_planner_input(trip_details, preferences, context)
        
        # Run the agent
        result = await self.agent.ainvoke({"input": input_text})
        
        # Parse the result into structured itinerary
        itinerary = self._parse_itinerary(
            result["output"],
            trip_details["start_date"],
            trip_details["duration_days"]
        )
        
        logger.info(f"Created {len(itinerary)} day itinerary")
        return itinerary, result["output"]
    
    def _format_planner_input(
        self,
        trip_details: Dict[str, Any],
        preferences: Dict[str, Any],
        context: List[str]
    ) -> str:
        """Format the input for the travel planner."""
        
        context_text = "\n".join(context[:3]) if context else "No additional context available"
        
        return f"""Create a detailed itinerary for:

Destination: {trip_details.get('destination', 'Unknown')}
Dates: {trip_details.get('start_date', 'TBD')} for {trip_details.get('duration_days', '?')} days
Travelers: {trip_details.get('num_travelers', 1)} person(s)
Purpose: {trip_details.get('purpose', 'leisure')}

Preferences:
- Budget: {preferences.get('budget', 'moderate')}
- Travel Style: {preferences.get('travel_style', 'balanced')}
- Interests: {', '.join(preferences.get('interests', []))}
- Accommodation: {preferences.get('accommodation_type', 'hotel')}

Relevant Information:
{context_text}

Please create a day-by-day itinerary with specific recommendations for activities, restaurants, and timing.
"""
    
    def _parse_itinerary(
        self,
        agent_output: str,
        start_date: Any,
        duration_days: Any
    ) -> List[Itinerary]:
        """
        Parse agent output into structured itinerary format.
        
        This is a simplified version - you may want to use more sophisticated
        parsing or ask the agent to return structured JSON.
        """
        itinerary = []
        
        # Ensure duration_days is an integer
        if isinstance(duration_days, str):
            try:
                duration_days = int(duration_days)
            except ValueError:
                duration_days = 1
        elif not isinstance(duration_days, int):
            duration_days = 1
            
        # Ensure start_date is a datetime object
        if isinstance(start_date, str):
            try:
                # Try parsing ISO format
                start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                # Try common formats
                try:
                    start_date = datetime.strptime(start_date, "%Y-%m-%d")
                except ValueError:
                    start_date = datetime.now()
        elif not isinstance(start_date, datetime):
            start_date = datetime.now()
        
        for day_num in range(1, duration_days + 1):
            current_date = start_date + timedelta(days=day_num - 1)
            
            # TODO: Implement proper parsing of agent output
            # For now, create placeholder structure
            itinerary.append(Itinerary(
                day=day_num,
                date=current_date,
                activities=[],
                meals=[],
                accommodation=None,
                notes=f"Day {day_num} activities from agent output"
            ))
        
        return itinerary
    
    async def modify_itinerary(
        self,
        current_itinerary: List[Itinerary],
        modification_request: str,
        state: ConversationState
    ) -> List[Itinerary]:
        """
        Modify an existing itinerary based on user feedback.
        
        Args:
            current_itinerary: Existing itinerary
            modification_request: User's modification request
            state: Current conversation state
        
        Returns:
            Updated itinerary
        """
        logger.info(f"Modifying itinerary: {modification_request}")
        
        input_text = f"""Current Itinerary:
{self._format_current_itinerary(current_itinerary)}

User Modification Request:
{modification_request}

Please update the itinerary based on the user's request while maintaining overall quality and coherence.
"""
        
        result = await self.agent.ainvoke({"input": input_text})
        
        # Parse updated itinerary
        updated_itinerary = self._parse_itinerary(
            result["output"],
            current_itinerary[0]["date"],
            len(current_itinerary)
        )
        
        return updated_itinerary
    
    def _format_current_itinerary(self, itinerary: List[Itinerary]) -> str:
        """Format current itinerary for display to the agent."""
        # TODO: Implement proper formatting
        return str(itinerary)
