"""
Centralized logging configuration for Telegram Job Scraper.

This module provides structured logging configuration with:
- Different log levels for different environments
- Structured log formatting with timestamps and context
- File and console handlers
- Rotating file handlers for production
- Error tracking and monitoring capabilities
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Custom log levels
VERBOSE = 15
logging.addLevelName(VERBOSE, "VERBOSE")

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    enable_console: bool = True,
    enable_file: bool = True,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Setup centralized logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        enable_console: Enable console logging
        enable_file: Enable file logging
        max_file_size: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
        
    Returns:
        Configured logger instance
    """
    
    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        logger.addHandler(console_handler)
    
    # File handler with rotation
    if enable_file and log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    # Error file handler (separate file for errors only)
    if enable_file and log_file:
        error_log_file = str(Path(log_file).with_suffix('.error.log'))
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        logger.addHandler(error_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

class StructuredLogger:
    """
    Structured logger with context and additional metadata.
    """
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.context = {}
    
    def bind(self, **kwargs) -> 'StructuredLogger':
        """Bind context data to the logger."""
        new_logger = StructuredLogger(self.logger.name)
        new_logger.context = {**self.context, **kwargs}
        return new_logger
    
    def _format_message(self, message: str) -> str:
        """Format message with context."""
        if self.context:
            context_str = " | ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{message} | {context_str}"
        return message
    
    def debug(self, message: str, **kwargs):
        """Log debug message with context."""
        self.logger.debug(self._format_message(message), extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message with context."""
        self.logger.info(self._format_message(message), extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with context."""
        self.logger.warning(self._format_message(message), extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with context."""
        self.logger.error(self._format_message(message), extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message with context."""
        self.logger.critical(self._format_message(message), extra=kwargs)
    
    def exception(self, message: str, **kwargs):
        """Log exception with traceback."""
        self.logger.exception(self._format_message(message), extra=kwargs)

# Performance monitoring
class PerformanceLogger:
    """Logger for performance metrics and timing."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(f"{name}.performance")
    
    def log_timing(self, operation: str, duration: float, **kwargs):
        """Log operation timing."""
        self.logger.info(
            f"Performance: {operation} took {duration:.3f}s",
            extra={"operation": operation, "duration": duration, **kwargs}
        )
    
    def log_memory_usage(self, memory_mb: float, **kwargs):
        """Log memory usage."""
        self.logger.info(
            f"Memory usage: {memory_mb:.2f}MB",
            extra={"memory_mb": memory_mb, **kwargs}
        )

# Initialize default logging
def init_default_logging():
    """Initialize default logging configuration."""
    log_file = os.getenv('LOG_FILE', 'logs/telegram_scraper.log')
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    return setup_logging(
        log_level=log_level,
        log_file=log_file,
        enable_console=True,
        enable_file=True
    ) 