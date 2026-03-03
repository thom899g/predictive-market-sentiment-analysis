"""
Robust logging configuration for ecosystem tracking.
Uses structlog for structured logging with context.
"""
import structlog
import logging
import sys
from typing import Dict, Any
from datetime import datetime

def configure_logging(log_level: str = "INFO", log_format: str = "json"):
    """
    Configure structured logging with error handling
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Output format (json, console)
    
    Raises:
        ValueError: If invalid log level or format provided
    """
    try:
        # Convert string log level to logging constant
        level = getattr(logging, log_level.upper(), None)
        if level is None:
            raise ValueError(f"Invalid log level: {log_level}")
        
        # Configure standard logging
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=level
        )
        
        # Configure structlog processors
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
        ]
        
        if log_format == "json":
            processors.append(structlog.processors.JSONRenderer())
        else:
            processors.append(structlog.dev.ConsoleRenderer())
        
        structlog.configure(
            processors=processors,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
        
        logger = structlog.get_logger()
        logger.info("logging_configured", 
                    log_level=log_level, 
                    log_format=log_format,
                    timestamp=datetime.utcnow().isoformat())
        
    except Exception as e:
        # Fallback to basic logging if configuration fails
        logging.basicConfig(level=logging.INFO)
        logging.error(f"Logging configuration failed: {str(e)}")
        raise

class LogContext:
    """Context manager for adding contextual information to logs"""
    
    def __init__(self, **context_vars):
        self.context_vars = context_vars
        self.old_context = {}
    
    def __enter__(self):
        logger = structlog.get_logger()
        self.old_context = logger._context._dict.copy()
        logger._context._dict.update(self.context_vars)
        return logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        logger = structlog.get_logger()
        logger._context._dict.clear()
        logger._context._dict.update(self.old_context)

def get_logger(name: str = None):