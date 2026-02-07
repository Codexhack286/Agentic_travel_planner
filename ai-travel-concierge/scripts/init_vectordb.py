#!/usr/bin/env python
"""
Initialize vector database with sample travel data.
"""
import logging
from pathlib import Path

from dotenv import load_dotenv

from src.utils.config import load_config
from src.utils.logger import setup_logger
from src.retrievers.rag.travel_retriever import TravelRetriever

# Setup
load_dotenv()
logger = setup_logger(__name__)


def load_sample_data():
    """Load sample travel data for the vector store."""
    
    sample_destinations = [
        {
            "text": """Paris, France is one of the world's most popular tourist destinations.
            Known as the City of Light, Paris offers iconic landmarks like the Eiffel Tower,
            Louvre Museum, Notre-Dame Cathedral, and Arc de Triomphe. The city is famous for
            its café culture, haute cuisine, fashion, and art. Best visited in spring (April-June)
            or fall (September-November) to avoid crowds. Must-try experiences include Seine river
            cruises, visiting Montmartre, exploring the Latin Quarter, and enjoying croissants
            at a local boulangerie.""",
            "metadata": {
                "destination": "Paris",
                "country": "France",
                "category": "overview",
                "interests": ["culture", "food", "art", "history"]
            }
        },
        {
            "text": """Tokyo, Japan seamlessly blends ancient traditions with modern technology.
            From serene temples and gardens to bustling districts like Shibuya and Shinjuku,
            Tokyo offers endless exploration. Key attractions include Senso-ji Temple, Tokyo
            Skytree, Meiji Shrine, and teamLab Borderless. Food lovers must try sushi at
            Tsukiji Market, ramen in local shops, and kaiseki dining. Best times to visit
            are spring (cherry blossoms) and autumn (fall foliage). The city has excellent
            public transportation with the JR Pass being essential for tourists.""",
            "metadata": {
                "destination": "Tokyo",
                "country": "Japan",
                "category": "overview",
                "interests": ["culture", "food", "technology", "temples"]
            }
        },
        {
            "text": """Bali, Indonesia is a tropical paradise known for stunning beaches, rice terraces,
            and spiritual culture. Popular areas include Ubud (cultural heart), Seminyak (beaches),
            Canggu (surf), and Uluwatu (cliffs). Must-visit sites include Tanah Lot Temple,
            Tegalalang Rice Terraces, and Sacred Monkey Forest. Best visited during dry season
            (April-October). Activities include surfing, diving, yoga retreats, and temple visits.
            Budget-friendly destination with options from backpacker hostels to luxury resorts.""",
            "metadata": {
                "destination": "Bali",
                "country": "Indonesia",
                "category": "overview",
                "interests": ["beach", "culture", "adventure", "wellness"]
            }
        },
        {
            "text": """New York City, USA is the city that never sleeps. Major attractions include
            Statue of Liberty, Central Park, Times Square, Empire State Building, and Metropolitan
            Museum of Art. Five boroughs offer distinct experiences: Manhattan (iconic landmarks),
            Brooklyn (trendy neighborhoods), Queens (diverse food), Bronx (zoo and gardens),
            Staten Island (ferry views). Best visited spring or fall. Excellent public transit
            via subway. Must-try foods include pizza, bagels, and diverse international cuisine.""",
            "metadata": {
                "destination": "New York",
                "country": "USA",
                "category": "overview",
                "interests": ["culture", "food", "shopping", "museums"]
            }
        },
        {
            "text": """Budget Travel Tips: Book flights 2-3 months in advance for best prices.
            Use flight comparison sites and be flexible with dates. Consider budget airlines
            for short-haul flights. Accommodations: hostels, Airbnb, and guesthouses save money.
            Eat like locals at markets and street food stalls. Use public transportation instead
            of taxis. Free walking tours available in most cities. Visit museums on free days.
            Travel during shoulder season for lower prices and fewer crowds.""",
            "metadata": {
                "category": "tips",
                "topic": "budget",
                "interests": ["budget"]
            }
        },
        {
            "text": """Luxury Travel Experiences: Five-star hotels and resorts with personalized service.
            Private tours with expert guides. First-class or business flights for comfort.
            Michelin-starred dining experiences. Exclusive access to attractions. Private yacht
            charters and helicopter tours. Luxury safari lodges. Personal shoppers and spa
            treatments. Concierge services for seamless planning. Worth splurging on unique
            once-in-a-lifetime experiences.""",
            "metadata": {
                "category": "tips",
                "topic": "luxury",
                "interests": ["luxury"]
            }
        }
    ]
    
    return sample_destinations


def initialize_vector_db():
    """Initialize the vector database with sample data."""
    
    logger.info("Starting vector database initialization...")
    
    try:
        # Load configuration
        config = load_config()
        
        # Create retriever (this initializes the vector store)
        retriever = TravelRetriever(config)
        
        # Load sample data
        sample_data = load_sample_data()
        
        # Extract texts and metadata
        texts = [item["text"] for item in sample_data]
        metadatas = [item["metadata"] for item in sample_data]
        
        # Add to vector store
        logger.info(f"Adding {len(texts)} documents to vector store...")
        ids = retriever.add_texts(texts=texts, metadatas=metadatas)
        
        logger.info(f"Successfully added {len(ids)} documents")
        
        # Test retrieval
        logger.info("Testing retrieval...")
        test_query = "I want to visit a city with great food and culture"
        results = retriever.retrieve(query=test_query, k=3)
        
        logger.info(f"Test query returned {len(results)} results")
        for i, doc in enumerate(results, 1):
            logger.info(f"  {i}. {doc.metadata.get('destination', 'N/A')}")
        
        # Print stats
        stats = retriever.get_stats()
        logger.info(f"Vector store stats: {stats}")
        
        logger.info("✓ Vector database initialization complete!")
        
    except Exception as e:
        logger.error(f"Error initializing vector database: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    initialize_vector_db()
