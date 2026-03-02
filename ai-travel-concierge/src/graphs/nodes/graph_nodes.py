"""
Node functions for the Travel Concierge LangGraph workflow.
"""
from typing import Dict, Any
import logging

from langchain_core.messages import HumanMessage, AIMessage
from langchain_groq import ChatGroq

from src.graphs.state.conversation_state import ConversationState
from src.agents.travel_planner.planner_agent import TravelPlannerAgent
from src.agents.recommendation_engine.recommender_agent import RecommenderAgent
from src.agents.booking_assistant.booking_agent import BookingAgent
from src.retrievers.rag.travel_retriever import TravelRetriever
from src.tools.external_apis.amadeus_tools import FlightSearchTool, HotelSearchTool
from src.tools.external_apis.weather_tools import WeatherForecastTool
from src.tools.external_apis.country_tools import CountryInfoTool
from src.tools.external_apis.currency_tools import CurrencyConversionTool
from src.tools.external_apis.visa_tools import VisaRequirementTool
from src.tools.external_apis.image_tools import UnsplashImageTool

logger = logging.getLogger(__name__)


class GraphNodes:
    """Collection of node functions for the travel concierge graph."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm = ChatGroq(
            model=config.get("model_name", "openai/gpt-oss-120b"),
            temperature=config.get("temperature", 0.7)
        )
        self.travel_planner = TravelPlannerAgent(config)
        self.recommender = RecommenderAgent(config)
        self.booking_agent = BookingAgent(config)
        self.retriever = TravelRetriever(config)
        
        # Initialize external API tools
        self.flight_tool = FlightSearchTool()
        self.hotel_tool = HotelSearchTool()
        self.weather_tool = WeatherForecastTool()
        self.country_tool = CountryInfoTool()
        self.currency_tool = CurrencyConversionTool()
        self.visa_tool = VisaRequirementTool()
        self.image_tool = UnsplashImageTool()
    
    async def classify_intent_node(self, state: ConversationState) -> ConversationState:
        """
        Classify user intent and extract travel entities from the conversation history.
        """
        logger.info("Node: Classifying user intent and extracting entities")
        
        # Combine recent messages to track clarifications and context
        recent_messages = state["messages"][-5:]
        conversation_context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])
        
        prompt = f"""You are a travel assistant. 
        Analyze the conversation and extract the user's main intent and any provided travel details.
        
        Conversation Context:
        {conversation_context}
        
        Possible intents:
        - plan_trip
        - get_recommendations
        - book_travel
        - modify_itinerary
        - ask_question
        - search_flights
        - search_hotels
        - check_weather
        - get_country_info
        - convert_currency
        - check_visa
        
        Respond ONLY with a raw JSON object (no markdown, no backticks, no extra text) with this structure:
        {{
            "intent": "the_intent",
            "destination": "city or country name" or null,
            "start_date": "YYYY-MM-DD" or null,
            "duration_days": integer or null,
            "budget": "budget level (e.g. moderate, luxury)" or null
        }}"""
        
        try:
            response = await self.llm.ainvoke(prompt)
            content = response.content.strip()
            
            # Remove any markdown formatting if the LLM stubbornly adds it
            if content.startswith("```json"): content = content.replace("```json", "", 1)
            if content.startswith("```"): content = content.replace("```", "", 1)
            if content.endswith("```"): content = content[:-3]
            
            import json
            data = json.loads(content.strip())
            
            intent = data.get("intent", "ask_question")
            if not isinstance(intent, str): intent = "ask_question"
            
            state["current_intent"] = intent.lower()
            logger.info(f"Classified intent: {state['current_intent']}")
            
            # Update state with newly found entities
            if data.get("destination"):
                state["trip_details"]["destination"] = str(data["destination"])
            if data.get("start_date"):
                # Simplification: store directly as string for now instead of datetime object parsing rules
                state["trip_details"]["start_date"] = str(data["start_date"])
            if data.get("duration_days") is not None:
                try:
                    state["trip_details"]["duration_days"] = int(data["duration_days"])
                except ValueError:
                    pass
            if data.get("budget"):
                state["user_preferences"]["budget"] = str(data["budget"])
                
            # Reset needs_more_info so the check_info node can accurately re-verify
            state["needs_more_info"] = False
            
        except Exception as e:
            logger.error(f"Failed to parse intent/entities from LLM: {e}")
            state["current_intent"] = "ask_question"
            
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
        itinerary, response_message = await self.travel_planner.create_itinerary(state)
        
        state["itinerary"] = itinerary
        state["needs_more_info"] = False
        
        # Add response to messages
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
        recommendations, response_message = await self.recommender.get_recommendations(state)
        
        state["recommendations"] = recommendations
        
        # Add response to messages
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
        response_message = booking_result.get("confirmation_details", self._format_booking_response(booking_result))
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
    
    async def flight_search_node(self, state: ConversationState) -> ConversationState:
        """Execute flight search based on extracted info."""
        logger.info("Node: Processing flight search")
        
        latest_message = state["messages"][-1]["content"]
        
        # Prompt LLM to extract flight search arguments
        prompt = f"""Extract flight search parameters from the user's message.
        User message: {latest_message}
        
        Required fields (if missing, try to infer or leave blank for clarification):
        - origin (IATA code)
        - destination (IATA code)
        - departure_date (YYYY-MM-DD)
        - return_date (YYYY-MM-DD, optional)
        
        Respond with a JSON object containing these keys."""
        
        # Simulating extraction... in a real app, use structured output parsing
        try:
            # Simple assumption for demo: The planner Agent or LLM parsed it, or we extract parameters roughly.
            # To keep things robust, we use the tool's arg schema via LLM structured generation
            function_call = await self.llm.bind_tools([self.flight_tool]).ainvoke(
                [HumanMessage(content=prompt)]
            )
            
            if function_call.tool_calls:
                kwargs = function_call.tool_calls[0]["args"]
                flight_results = await self.flight_tool._call_api(**kwargs)
                normalized = self.flight_tool._normalize_response(flight_results)
                
                state["messages"].append({
                    "role": "assistant",
                    "content": f"I found {normalized.get('count', 0)} flight options for you."
                })
            else:
                 state["messages"].append({
                    "role": "assistant",
                    "content": "I couldn't extract all the necessary flight details. Could you provide the origin, destination, and dates?"
                })
                
        except Exception as e:
            logger.error(f"Flight search error: {e}")
            state["messages"].append({"role": "assistant", "content": "Failed to search for flights."})
        
        return state

    async def hotel_search_node(self, state: ConversationState) -> ConversationState:
        """Execute hotel search."""
        logger.info("Node: Processing hotel search")
        latest_message = state["messages"][-1]["content"]
        prompt = f"Extract hotel search parameters: city_code (IATA), check_in, check_out, adults.\nMessage: {latest_message}"
        
        try:
            function_call = await self.llm.bind_tools([self.hotel_tool]).ainvoke([HumanMessage(content=prompt)])
            if function_call.tool_calls:
                kwargs = function_call.tool_calls[0]["args"]
                hotel_results = await self.hotel_tool._call_api(**kwargs)
                normalized = self.hotel_tool._normalize_response(hotel_results)
                state["messages"].append({
                    "role": "assistant",
                    "content": f"I found {normalized.get('count', 0)} hotel options for you."
                })
            else:
                state["messages"].append({"role": "assistant", "content": "I need more details (city, dates) to search for hotels."})
        except Exception as e:
            logger.error(f"Hotel search error: {e}")
            state["messages"].append({"role": "assistant", "content": "Failed to search for hotels."})
            
        return state

    async def weather_check_node(self, state: ConversationState) -> ConversationState:
        """Execute weather check."""
        logger.info("Node: Checking weather")
        latest_message = state["messages"][-1]["content"]
        prompt = f"Extract weather parameters: destination, start_date, end_date.\nMessage: {latest_message}"
        
        try:
            function_call = await self.llm.bind_tools([self.weather_tool]).ainvoke([HumanMessage(content=prompt)])
            if function_call.tool_calls:
                kwargs = function_call.tool_calls[0]["args"]
                weather_results = await self.weather_tool._call_api(**kwargs)
                normalized = self.weather_tool._normalize_response(weather_results)
                state["messages"].append({"role": "assistant", "content": f"Here is the weather forecast for {kwargs.get('destination')}."})
            else:
                state["messages"].append({"role": "assistant", "content": "Could you specify the destination and dates for the weather forecast?"})
        except Exception as e:
            logger.error(f"Weather check error: {e}")
            state["messages"].append({"role": "assistant", "content": "Failed to check weather."})
            
        return state

    async def country_info_node(self, state: ConversationState) -> ConversationState:
        """Execute country info check."""
        logger.info("Node: Checking country info")
        latest_message = state["messages"][-1]["content"]
        prompt = f"Extract country query from message.\nMessage: {latest_message}"
        
        try:
            function_call = await self.llm.bind_tools([self.country_tool]).ainvoke([HumanMessage(content=prompt)])
            if function_call.tool_calls:
                kwargs = function_call.tool_calls[0]["args"]
                info = await self.country_tool._call_api(**kwargs)
                normalized = self.country_tool._normalize_response(info)
                state["messages"].append({"role": "assistant", "content": f"Country Information: {normalized.get('name', {}).get('common')}."})
        except Exception as e:
            logger.error(f"Country info error: {e}")
            state["messages"].append({"role": "assistant", "content": "Failed to retrieve country information."})
            
        return state

    async def currency_conversion_node(self, state: ConversationState) -> ConversationState:
        """Execute currency conversion."""
        logger.info("Node: Converting currency")
        latest_message = state["messages"][-1]["content"]
        prompt = f"Extract currency parameters: amount, from_currency, to_currency.\nMessage: {latest_message}"
        
        try:
            function_call = await self.llm.bind_tools([self.currency_tool]).ainvoke([HumanMessage(content=prompt)])
            if function_call.tool_calls:
                kwargs = function_call.tool_calls[0]["args"]
                result = await self.currency_tool._call_api(**kwargs)
                normalized = self.currency_tool._normalize_response(result)
                state["messages"].append({"role": "assistant", "content": f"Currency Conversion: {normalized.get('formula')}"})
        except Exception as e:
            logger.error(f"Currency error: {e}")
            state["messages"].append({"role": "assistant", "content": "Failed to convert currency."})
            
        return state

    async def visa_requirement_node(self, state: ConversationState) -> ConversationState:
        """Execute visa requirement check."""
        logger.info("Node: Checking visa requirements")
        latest_message = state["messages"][-1]["content"]
        prompt = f"Extract visa check parameters: from_country (2-letter ISO), to_country (2-letter ISO).\nMessage: {latest_message}"
        
        try:
            function_call = await self.llm.bind_tools([self.visa_tool]).ainvoke([HumanMessage(content=prompt)])
            if function_call.tool_calls:
                kwargs = function_call.tool_calls[0]["args"]
                result = await self.visa_tool._call_api(**kwargs)
                normalized = self.visa_tool._normalize_response(result)
                state["messages"].append({"role": "assistant", "content": f"Visa Requirement: {normalized.get('summary')}"})
        except Exception as e:
            logger.error(f"Visa check error: {e}")
            state["messages"].append({"role": "assistant", "content": "Failed to check visa requirements."})
            
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
