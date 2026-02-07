"""
AI Travel Concierge - Main Application Entry Point
"""
import asyncio
import logging
from pathlib import Path

from dotenv import load_dotenv

from src.graphs.workflows.travel_concierge_graph import TravelConciergeGraph
from src.utils.logger import setup_logger
from src.utils.config import load_config

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logger(__name__)


async def main():
    """Main application entry point."""
    logger.info("Starting AI Travel Concierge...")
    
    try:
        # Load configuration
        config = load_config()
        
        # Initialize the travel concierge graph
        travel_graph = TravelConciergeGraph(config)
        
        # Example interaction
        user_input = "I want to plan a 5-day trip to Paris"
        
        logger.info(f"Processing user request: {user_input}")
        
        # Run the graph
        result = await travel_graph.run(user_input)
        
        logger.info(f"Response: {result}")
        
    except Exception as e:
        logger.error(f"Error in main application: {e}", exc_info=True)
        raise


def run_cli():
    """Run interactive CLI mode."""
    print("=== AI Travel Concierge ===")
    print("Type 'exit' to quit\n")
    
    config = load_config()
    travel_graph = TravelConciergeGraph(config)
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("Thank you for using AI Travel Concierge. Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Run synchronously for CLI
            result = asyncio.run(travel_graph.run(user_input))
            print(f"\nAssistant: {result}\n")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            print(f"Error: {e}\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        run_cli()
    else:
        asyncio.run(main())
