"""
Centralized logging configuration for the Telegram Job Scraper.

This module provides structured logging configuration with different handlers
for console, file, and optional external services.
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import json
from datetime import datetime

class StructuredFormatter(logging.Formatter):
    """Custom formatter that outputs structured JSON logs for better parsing."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry, ensure_ascii=False)

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output for console."""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format the message
        formatted = super().format(record)
        
        # Add color to level name
        formatted = formatted.replace(
            record.levelname,
            f"{color}{record.levelname}{reset}"
        )
        
        return formatted

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_dir: str = "logs",
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    enable_console: bool = True,
    enable_file: bool = True,
    enable_json: bool = False,
    enable_colors: bool = True
) -> logging.Logger:
    """
    Setup comprehensive logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Log file path (relative to log_dir)
        log_dir: Directory for log files
        max_file_size: Maximum size of log files before rotation
        backup_count: Number of backup files to keep
        enable_console: Enable console logging
        enable_file: Enable file logging
        enable_json: Enable JSON structured logging
        enable_colors: Enable colored console output
    
    Returns:
        Configured root logger
    """
    # Create log directory if it doesn't exist
    if enable_file:
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)
    
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        
        if enable_colors and not enable_json:
            formatter = ColoredFormatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        elif enable_json:
            formatter = StructuredFormatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if enable_file:
        if not log_file:
            log_file = f"telegram_scraper_{datetime.now().strftime('%Y%m%d')}.log"
        
        file_path = Path(log_dir) / log_file
        
        # Use rotating file handler for better log management
        file_handler = logging.handlers.RotatingFileHandler(
            file_path,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        
        if enable_json:
            formatter = StructuredFormatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
        
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Add custom logger for the application
    app_logger = logging.getLogger('telegram_scraper')
    app_logger.setLevel(getattr(logging, log_level.upper()))
    
    return app_logger

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)

def log_function_call(logger: logging.Logger):
    """
    Decorator to log function calls with parameters and return values.
    
    Args:
        logger: Logger instance to use
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Log function entry
            logger.debug(f"Entering {func.__name__} with args={args}, kwargs={kwargs}")
            
            try:
                result = func(*args, **kwargs)
                logger.debug(f"Exiting {func.__name__} with result={result}")
                return result
            except Exception as e:
                logger.error(f"Exception in {func.__name__}: {e}", exc_info=True)
                raise
        
        return wrapper
    return decorator

def log_performance(logger: logging.Logger):
    """
    Decorator to log function performance metrics.
    
    Args:
        logger: Logger instance to use
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(f"{func.__name__} executed in {execution_time:.4f} seconds")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"{func.__name__} failed after {execution_time:.4f} seconds: {e}")
                raise
        
        return wrapper
    return decorator

class ErrorTracker:
    """Track and report errors with context."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.error_count = 0
        self.error_types = {}
    
    def track_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """
        Track an error with optional context.
        
        Args:
            error: The exception that occurred
            context: Optional context dictionary
        """
        self.error_count += 1
        error_type = type(error).__name__
        self.error_types[error_type] = self.error_types.get(error_type, 0) + 1
        
        # Log the error with context
        extra_fields = {
            'error_type': error_type,
            'error_count': self.error_count,
            'context': context or {}
        }
        
        self.logger.error(
            f"Error #{self.error_count} ({error_type}): {str(error)}",
            extra={'extra_fields': extra_fields},
            exc_info=True
        )
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get a summary of tracked errors."""
        return {
            'total_errors': self.error_count,
            'error_types': self.error_types.copy(),
            'most_common_error': max(self.error_types.items(), key=lambda x: x[1]) if self.error_types else None
        }

# Global error tracker instance
error_tracker = ErrorTracker(get_logger('error_tracker'))

def log_error(error: Exception, context: Optional[Dict[str, Any]] = None):
    """
    Convenience function to log errors with the global error tracker.
    
    Args:
        error: The exception to log
        context: Optional context dictionary
    """
    error_tracker.track_error(error, context) 