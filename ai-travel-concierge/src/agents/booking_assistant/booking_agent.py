"""
Booking Assistant Agent - Handles travel bookings and reservations.
"""
import logging
from typing import Dict, Any
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from src.graphs.state.conversation_state import ConversationState
from src.tools.external_apis.booking_tool import BookingTool

logger = logging.getLogger(__name__)


class BookingAgent:
    """
    Specialized agent for handling travel bookings.
    
    Manages:
    - Flight bookings
    - Hotel reservations
    - Activity bookings
    - Tour reservations
    - Payment processing coordination
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm = ChatOpenAI(
            model=config.get("model_name", "gpt-4-turbo-preview"),
            temperature=0.3  # Lower temperature for booking accuracy
        )
        
        # Initialize tools
        self.tools = [
            BookingTool(),
        ]
        
        # Create agent
        self.agent = self._create_agent()
        
        logger.info("Booking Agent initialized")
    
    def _create_agent(self) -> AgentExecutor:
        """Create the booking agent with tools."""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a professional travel booking assistant.
            
            Your role is to:
            1. Verify all booking details with the user
            2. Check availability and pricing
            3. Process bookings through appropriate channels
            4. Confirm reservations
            5. Provide booking references and documentation
            
            IMPORTANT:
            - ALWAYS verify details before making a booking
            - Double-check dates, times, and passenger information
            - Confirm pricing and payment terms
            - Explain cancellation policies
            - Provide clear confirmation with reference numbers
            
            Never make a booking without explicit user confirmation.
            
            Be precise, accurate, and professional in all booking interactions.
            """),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_functions_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True)
    
    async def process_booking(self, state: ConversationState) -> Dict[str, Any]:
        """
        Process a travel booking request.
        
        Args:
            state: Current conversation state
        
        Returns:
            Booking confirmation details
        """
        logger.info("Processing booking request")
        
        # Extract booking details from state
        booking_request = self._extract_booking_request(state)
        
        # Prepare input for agent
        input_text = self._format_booking_input(booking_request)
        
        # Run the agent
        result = await self.agent.ainvoke({"input": input_text})
        
        # Parse booking result
        booking_result = self._parse_booking_result(result["output"])
        
        logger.info(f"Booking processed: {booking_result.get('status')}")
        return booking_result
    
    async def verify_booking(
        self,
        booking_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Verify booking details before processing.
        
        Args:
            booking_details: Details to verify
        
        Returns:
            Verification result with any issues found
        """
        logger.info("Verifying booking details")
        
        input_text = f"""Please verify the following booking details:

{self._format_booking_details(booking_details)}

Check for:
- Correct dates and times
- Accurate passenger information
- Availability
- Current pricing
- Any restrictions or requirements

Provide a detailed verification report.
"""
        
        result = await self.agent.ainvoke({"input": input_text})
        
        return {
            "verified": True,  # TODO: Parse from result
            "issues": [],
            "verification_details": result["output"]
        }
    
    async def cancel_booking(
        self,
        booking_reference: str,
        reason: str = None
    ) -> Dict[str, Any]:
        """
        Cancel an existing booking.
        
        Args:
            booking_reference: Booking reference number
            reason: Optional cancellation reason
        
        Returns:
            Cancellation confirmation
        """
        logger.info(f"Canceling booking: {booking_reference}")
        
        input_text = f"""Please cancel the following booking:

Booking Reference: {booking_reference}
Cancellation Reason: {reason or 'Not specified'}

Process the cancellation and provide:
- Confirmation of cancellation
- Refund details (if applicable)
- Cancellation reference number
"""
        
        result = await self.agent.ainvoke({"input": input_text})
        
        return {
            "status": "cancelled",
            "booking_reference": booking_reference,
            "cancellation_details": result["output"],
            "timestamp": datetime.now().isoformat()
        }
    
    async def modify_booking(
        self,
        booking_reference: str,
        modifications: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Modify an existing booking.
        
        Args:
            booking_reference: Booking reference number
            modifications: Dictionary of changes to make
        
        Returns:
            Modification confirmation
        """
        logger.info(f"Modifying booking: {booking_reference}")
        
        input_text = f"""Please modify the following booking:

Booking Reference: {booking_reference}

Requested Changes:
{self._format_modifications(modifications)}

Process the modification and provide:
- Confirmation of changes
- Any price differences
- New booking details
- Updated reference number (if changed)
"""
        
        result = await self.agent.ainvoke({"input": input_text})
        
        return {
            "status": "modified",
            "booking_reference": booking_reference,
            "modification_details": result["output"],
            "timestamp": datetime.now().isoformat()
        }
    
    def _extract_booking_request(self, state: ConversationState) -> Dict[str, Any]:
        """Extract booking request from conversation state."""
        
        latest_message = state["messages"][-1]["content"]
        
        # Extract what user wants to book
        # This could be enhanced with NER or structured extraction
        
        return {
            "type": "unknown",  # flight, hotel, activity, package
            "details": state.get("recommendations", {}),
            "user_message": latest_message,
            "trip_details": state["trip_details"]
        }
    
    def _format_booking_input(self, booking_request: Dict[str, Any]) -> str:
        """Format booking request for agent input."""
        
        return f"""Process the following booking request:

Type: {booking_request.get('type', 'To be determined')}
User Request: {booking_request.get('user_message')}

Trip Details:
{self._format_booking_details(booking_request.get('trip_details', {}))}

Before proceeding:
1. Verify all details are correct
2. Check availability and current pricing
3. Confirm with user if anything is unclear
4. Process the booking only after user confirmation
"""
    
    def _format_booking_details(self, details: Dict[str, Any]) -> str:
        """Format booking details for display."""
        lines = []
        for key, value in details.items():
            if value:
                lines.append(f"- {key.replace('_', ' ').title()}: {value}")
        return "\n".join(lines)
    
    def _format_modifications(self, modifications: Dict[str, Any]) -> str:
        """Format modification requests."""
        lines = []
        for key, value in modifications.items():
            lines.append(f"- Change {key.replace('_', ' ')}: {value}")
        return "\n".join(lines)
    
    def _parse_booking_result(self, agent_output: str) -> Dict[str, Any]:
        """Parse booking result from agent output."""
        
        # TODO: Implement sophisticated parsing
        # Should extract: status, reference number, pricing, confirmation details
        
        return {
            "status": "pending",
            "booking_reference": "TBD",
            "confirmation_details": agent_output,
            "timestamp": datetime.now().isoformat()
        }
