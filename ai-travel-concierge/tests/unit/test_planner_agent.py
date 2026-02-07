"""
Unit tests for Travel Planner Agent.
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from src.agents.travel_planner.planner_agent import TravelPlannerAgent
from src.graphs.state.conversation_state import ConversationState, create_initial_state


@pytest.fixture
def config():
    """Test configuration."""
    return {
        "model_name": "gpt-4-turbo-preview",
        "temperature": 0.7,
        "openai_api_key": "test-key"
    }


@pytest.fixture
def sample_state():
    """Sample conversation state."""
    state = create_initial_state(user_id="test-user")
    
    state["trip_details"]["destination"] = "Paris"
    state["trip_details"]["start_date"] = datetime.now() + timedelta(days=30)
    state["trip_details"]["duration_days"] = 5
    state["trip_details"]["num_travelers"] = 2
    
    state["user_preferences"]["budget"] = "moderate"
    state["user_preferences"]["travel_style"] = "cultural"
    state["user_preferences"]["interests"] = ["museums", "food", "architecture"]
    
    return state


class TestTravelPlannerAgent:
    """Test suite for Travel Planner Agent."""
    
    def test_agent_initialization(self, config):
        """Test agent initializes correctly."""
        agent = TravelPlannerAgent(config)
        
        assert agent is not None
        assert agent.llm is not None
        assert len(agent.tools) > 0
    
    @pytest.mark.asyncio
    async def test_create_itinerary(self, config, sample_state):
        """Test itinerary creation."""
        agent = TravelPlannerAgent(config)
        
        with patch.object(agent.agent, 'ainvoke') as mock_invoke:
            mock_invoke.return_value = {
                "output": "Day 1: Visit Louvre..."
            }
            
            itinerary = await agent.create_itinerary(sample_state)
            
            assert itinerary is not None
            assert len(itinerary) == 5  # 5 days
            assert mock_invoke.called
    
    def test_format_planner_input(self, config, sample_state):
        """Test input formatting."""
        agent = TravelPlannerAgent(config)
        
        trip_details = sample_state["trip_details"]
        preferences = sample_state["user_preferences"]
        context = ["Paris is known for..."]
        
        formatted_input = agent._format_planner_input(
            trip_details,
            preferences,
            context
        )
        
        assert "Paris" in formatted_input
        assert "cultural" in formatted_input
        assert "museums" in formatted_input
