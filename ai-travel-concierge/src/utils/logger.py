"""
Logging configuration and utilities.
"""
import sys
import logging
from pathlib import Path
from typing import Optional

from loguru import logger as loguru_logger


def setup_logger(
    name: str,
    log_level: str = "INFO",
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Set up a logger with consistent formatting.
    
    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
    
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def setup_loguru(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    rotation: str = "100 MB",
    retention: str = "10 days"
):
    """
    Set up Loguru logger with advanced features.
    
    Args:
        log_level: Logging level
        log_file: Optional path to log file
        rotation: When to rotate log files
        retention: How long to keep old log files
    """
    # Remove default handler
    loguru_logger.remove()
    
    # Add console handler
    loguru_logger.add(
        sys.stdout,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # Add file handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        loguru_logger.add(
            log_file,
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation=rotation,
            retention=retention,
            compression="zip"
        )


class LoggerAdapter:
    """
    Adapter to use Loguru with LangChain's logging expectations.
    """
    
    def __init__(self, logger_name: str = "langchain"):
        self.logger_name = logger_name
    
    def debug(self, msg: str, *args, **kwargs):
        loguru_logger.bind(name=self.logger_name).debug(msg, *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs):
        loguru_logger.bind(name=self.logger_name).info(msg, *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs):
        loguru_logger.bind(name=self.logger_name).warning(msg, *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs):
        loguru_logger.bind(name=self.logger_name).error(msg, *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs):
        loguru_logger.bind(name=self.logger_name).critical(msg, *args, **kwargs)


def configure_langchain_logging():
    """Configure logging for LangChain components."""
    import langchain
    
    # Set LangChain verbosity
    langchain.verbose = True
    
    # Use custom logger adapter
    langchain_logger = LoggerAdapter("langchain")
    
    return langchain_logger
