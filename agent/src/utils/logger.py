"""
Terra Scout Logger Utility
"""

import logging
import sys
from typing import Optional


def get_logger(name: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (usually __name__)
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name or "terra_scout")
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
    
    return logger


# Default logger instance
logger = get_logger()
