"""
Configuration management utilities.
"""
import os
from typing import Dict, Any
from pathlib import Path

from pydantic_settings import BaseSettings
from dotenv import load_dotenv


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # LLM Settings
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""
    model_name: str = "gpt-4-turbo-preview"
    temperature: float = 0.7
    max_tokens: int = 4000
    
    # LangSmith Settings
    langchain_tracing_v2: bool = False
    langchain_endpoint: str = "https://api.smith.langchain.com"
    langchain_api_key: str = ""
    langchain_project: str = "ai-travel-concierge"
    
    # Vector Database Settings
    chroma_persist_directory: str = "./data/vector_db"
    collection_name: str = "travel_knowledge"
    embedding_model: str = "text-embedding-3-small"
    
    # RAG Settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_results: int = 5
    similarity_threshold: float = 0.7
    
    # Redis Settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    
    # Database Settings
    database_url: str = "sqlite:///./data/travel_concierge.db"
    
    # Travel API Settings
    amadeus_api_key: str = ""
    amadeus_api_secret: str = ""
    google_maps_api_key: str = ""
    weather_api_key: str = ""
    
    # Agent Settings
    max_iterations: int = 10
    agent_timeout: int = 120
    
    # Application Settings
    debug: bool = False
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def load_config() -> Dict[str, Any]:
    """
    Load configuration from environment variables and .env file.
    
    Returns:
        Dictionary with configuration settings
    """
    # Load .env file
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    
    # Create settings instance
    settings = Settings()
    
    # Convert to dictionary
    config = settings.model_dump()
    
    # Set environment variables for LangChain
    if config.get("langchain_tracing_v2"):
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_ENDPOINT"] = config["langchain_endpoint"]
        os.environ["LANGCHAIN_API_KEY"] = config["langchain_api_key"]
        os.environ["LANGCHAIN_PROJECT"] = config["langchain_project"]
    
    return config


def get_api_keys() -> Dict[str, str]:
    """
    Get all API keys from configuration.
    
    Returns:
        Dictionary of API keys
    """
    config = load_config()
    
    return {
        "openai": config.get("openai_api_key"),
        "anthropic": config.get("anthropic_api_key"),
        "google": config.get("google_api_key"),
        "amadeus_key": config.get("amadeus_api_key"),
        "amadeus_secret": config.get("amadeus_api_secret"),
        "google_maps": config.get("google_maps_api_key"),
        "weather": config.get("weather_api_key"),
    }


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate that required configuration is present.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        True if configuration is valid
    
    Raises:
        ValueError: If required configuration is missing
    """
    required_keys = [
        "openai_api_key",
        "model_name",
    ]
    
    missing = [key for key in required_keys if not config.get(key)]
    
    if missing:
        raise ValueError(f"Missing required configuration: {', '.join(missing)}")
    
    return True
