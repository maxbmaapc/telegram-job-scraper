import os
import logging
import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

from .logging_config import get_logger, setup_logging

# Load environment variables
load_dotenv()

class ConfigValidationError(Exception):
    """Custom exception for configuration validation errors."""
    pass

class Config:
    """Enhanced configuration class for the Telegram Job Scraper"""
    
    def __init__(self):
        # Initialize logging first
        self._setup_logging()
        self.logger = get_logger(__name__)
        
        # Telegram API Credentials
        self.api_id = self._get_required_env('API_ID')
        self.api_hash = self._get_required_env('API_HASH')
        self.phone_number = self._get_required_env('PHONE_NUMBER')
        
        # Target Channels
        self.target_channels = self._parse_list_env('TARGET_CHANNELS')
        
        # Target Personal Account (where to send messages)
        self.target_user_id = os.getenv('TARGET_USER_ID')
        self.target_username = os.getenv('TARGET_USERNAME')
        self.target_phone_number = os.getenv('TARGET_PHONE_NUMBER')
        
        # Filter Settings
        self.filter_keywords = self._parse_list_env('FILTER_KEYWORDS')
        self.date_filter_hours = int(os.getenv('DATE_FILTER_HOURS', '24'))
        
        # Output Settings
        self.output_method = os.getenv('OUTPUT_METHOD', 'telegram').lower()
        self.send_to_self = os.getenv('SEND_TO_SELF', 'false').lower() == 'true'  # Changed default to false
        
        # Rate Limiting Settings (to avoid Telegram bans)
        self.message_delay_min = float(os.getenv('MESSAGE_DELAY_MIN', '2.0'))  # Minimum delay between messages
        self.message_delay_max = float(os.getenv('MESSAGE_DELAY_MAX', '3.0'))  # Maximum delay between messages
        
        # Database Settings
        self.database_path = os.getenv('DATABASE_PATH', 'jobs.db')
        
        # Logging
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_file = os.getenv('LOG_FILE', 'logs/telegram_scraper.log')
        
        # Web UI Settings
        self.web_host = os.getenv('WEB_HOST', 'localhost')
        self.web_port = int(os.getenv('WEB_PORT', '5000'))
        
        # Session file
        self.session_name = 'telegram_job_scraper'
        
        # Scheduling Settings
        self.schedule_interval_minutes = int(os.getenv('SCHEDULE_INTERVAL_MINUTES', '30'))
        self.schedule_start_time = os.getenv('SCHEDULE_START_TIME', None)  # e.g., "09:00"
        self.schedule_end_time = os.getenv('SCHEDULE_END_TIME', None)      # e.g., "18:00"
        self.schedule_days_of_week = self._parse_days_of_week(os.getenv('SCHEDULE_DAYS_OF_WEEK', '0,1,2,3,4,5,6'))
        self.schedule_max_runs_per_day = int(os.getenv('SCHEDULE_MAX_RUNS_PER_DAY', '0')) or None
        
        # Performance Settings
        self.batch_size = int(os.getenv('BATCH_SIZE', '50'))  # Messages to process in batches
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))  # Max retries for failed operations
        
        # Security Settings
        self.enable_ssl_verification = os.getenv('ENABLE_SSL_VERIFICATION', 'true').lower() == 'true'
        
        # Validate configuration
        self.validate()
    
    def _get_required_env(self, key: str) -> str:
        """Get a required environment variable with validation."""
        value = os.getenv(key)
        if not value:
            raise ConfigValidationError(f'Required environment variable {key} is not set')
        
        # Validate specific fields
        if key == 'API_ID' and not value.isdigit():
            raise ConfigValidationError(f'API_ID must be a numeric value, got: {value}')
        
        if key == 'API_HASH' and len(value) != 32:
            raise ConfigValidationError(f'API_HASH must be 32 characters long, got: {len(value)}')
        
        if key == 'PHONE_NUMBER' and not self._is_valid_phone_number(value):
            raise ConfigValidationError(f'Invalid phone number format: {value}. Use international format (e.g., +1234567890)')
        
        return value
    
    def _is_valid_phone_number(self, phone: str) -> bool:
        """Validate phone number format."""
        # Basic validation for international format
        if not phone.startswith('+'):
            return False
        
        # Remove + and check if rest is numeric
        digits = phone[1:].replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        return digits.isdigit() and len(digits) >= 10
    
    def _parse_list_env(self, key: str) -> List[str]:
        """Parse a comma-separated environment variable into a list with validation."""
        value = os.getenv(key, '')
        if not value:
            return []
        
        items = [item.strip() for item in value.split(',') if item.strip()]
        
        # Validate channel IDs if this is TARGET_CHANNELS
        if key == 'TARGET_CHANNELS':
            for item in items:
                if not self._is_valid_channel_id(item):
                    self.logger.warning(f'Potentially invalid channel ID: {item}')
        
        return items
    
    def _is_valid_channel_id(self, channel_id: str) -> bool:
        """Validate Telegram channel ID format."""
        try:
            # Channel IDs should be negative numbers starting with -100
            if not channel_id.startswith('-100'):
                return False
            
            # Check if the rest is numeric
            int(channel_id[4:])
            return True
        except ValueError:
            return False
    
    def _parse_days_of_week(self, value: str) -> List[int]:
        """Parse days of week string into list of integers with validation."""
        try:
            days = [int(day.strip()) for day in value.split(',') if day.strip()]
            
            # Validate day numbers (0=Sunday, 1=Monday, ..., 6=Saturday)
            for day in days:
                if day < 0 or day > 6:
                    raise ConfigValidationError(f'Invalid day of week: {day}. Must be 0-6 (0=Sunday, 6=Saturday)')
            
            return days
        except ValueError as e:
            raise ConfigValidationError(f'Invalid days of week format: {value}. Use comma-separated numbers 0-6')
    
    def _setup_logging(self):
        """Setup enhanced logging configuration."""
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        log_file = os.getenv('LOG_FILE', 'telegram_scraper.log')
        enable_json = os.getenv('LOG_JSON', 'false').lower() == 'true'
        enable_colors = os.getenv('LOG_COLORS', 'true').lower() == 'true'
        
        setup_logging(
            log_level=log_level,
            log_file=log_file,
            enable_console=True,
            enable_file=True,
            enable_json=enable_json,
            enable_colors=enable_colors
        )
    
    def get_target_entity(self) -> Optional[str]:
        """Get the target entity for sending messages."""
        if self.target_user_id:
            return self.target_user_id
        elif self.target_username:
            return self.target_username
        elif self.target_phone_number:
            return self.target_phone_number
        return None
    
    def validate(self) -> bool:
        """Comprehensive configuration validation with enhanced error reporting."""
        errors = []
        warnings = []
        
        # Validate Telegram credentials
        try:
            int(self.api_id)
        except ValueError:
            errors.append("API_ID must be a valid integer")
        
        if len(self.api_hash) != 32:
            errors.append("API_HASH must be exactly 32 characters long")
        
        if not self._is_valid_phone_number(self.phone_number):
            errors.append("PHONE_NUMBER must be in international format (e.g., +1234567890)")
        
        # Validate target channels
        if not self.target_channels:
            errors.append("No target channels configured. Set TARGET_CHANNELS environment variable")
        else:
            for channel_id in self.target_channels:
                if not self._is_valid_channel_id(channel_id):
                    errors.append(f"Invalid channel ID format: {channel_id}. Must start with -100")
        
        # Validate filter keywords with detailed feedback
        if not self.filter_keywords:
            errors.append("No filter keywords configured. Set FILTER_KEYWORDS environment variable")
        else:
            # Check for common issues with keywords
            for keyword in self.filter_keywords:
                if len(keyword) < 2:
                    warnings.append(f"Very short keyword '{keyword}' may cause false positives")
                if keyword.lower() in ['a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for']:
                    warnings.append(f"Common word '{keyword}' may cause false positives")
        
        # Validate date filter
        if self.date_filter_hours < 0:
            errors.append("DATE_FILTER_HOURS must be non-negative")
        elif self.date_filter_hours > 8760:  # More than 1 year
            warnings.append(f"Very long date filter ({self.date_filter_hours} hours) may impact performance")
        
        # Validate output method
        valid_output_methods = ['telegram', 'file', 'database']
        if self.output_method not in valid_output_methods:
            errors.append(f"Invalid OUTPUT_METHOD: {self.output_method}. Must be one of: {valid_output_methods}")
        
        # Validate target entity for Telegram output
        if self.output_method == 'telegram' and not self.send_to_self:
            if not self.get_target_entity():
                errors.append("No target entity configured for sending messages. Set TARGET_USER_ID, TARGET_USERNAME, or TARGET_PHONE_NUMBER")
        
        # Validate rate limiting settings
        if self.message_delay_min < 0 or self.message_delay_max < 0:
            errors.append("Message delay values must be non-negative")
        
        if self.message_delay_min > self.message_delay_max:
            errors.append("MESSAGE_DELAY_MIN cannot be greater than MESSAGE_DELAY_MAX")
        
        if self.message_delay_min < 1.0:
            warnings.append("Very low message delay may trigger Telegram rate limits")
        
        # Validate database path and permissions
        if self.output_method == 'database':
            self._validate_database_config(errors, warnings)
        
        # Validate web UI settings
        if self.web_port < 1 or self.web_port > 65535:
            errors.append(f"Invalid web port: {self.web_port}. Must be between 1 and 65535")
        elif self.web_port < 1024:
            warnings.append(f"Web port {self.web_port} requires root privileges on some systems")
        
        # Validate scheduling settings
        if self.schedule_interval_minutes < 1:
            errors.append("SCHEDULE_INTERVAL_MINUTES must be at least 1 minute")
        elif self.schedule_interval_minutes < 5:
            warnings.append(f"Very frequent scheduling ({self.schedule_interval_minutes} minutes) may impact performance")
        
        if self.schedule_start_time and self.schedule_end_time:
            try:
                from datetime import datetime
                start_time = datetime.strptime(self.schedule_start_time, '%H:%M')
                end_time = datetime.strptime(self.schedule_end_time, '%H:%M')
                if start_time >= end_time:
                    warnings.append("Schedule start time should be before end time")
            except ValueError:
                errors.append("Schedule times must be in HH:MM format (e.g., 09:00)")
        
        # Validate performance settings
        if self.batch_size < 1:
            errors.append("BATCH_SIZE must be at least 1")
        elif self.batch_size > 1000:
            warnings.append(f"Large batch size ({self.batch_size}) may cause memory issues")
        
        if self.max_retries < 0:
            errors.append("MAX_RETRIES must be non-negative")
        elif self.max_retries > 10:
            warnings.append(f"High retry count ({self.max_retries}) may cause excessive delays")
        
        # Validate security settings
        if not self.enable_ssl_verification:
            warnings.append("SSL verification is disabled - this may pose security risks")
        
        # Log warnings
        if warnings:
            for warning in warnings:
                self.logger.warning(f"Configuration warning: {warning}")
        
        # Raise exception if any errors found
        if errors:
            error_message = "Configuration validation failed:\n" + "\n".join(f"- {error}" for error in errors)
            raise ConfigValidationError(error_message)
        
        self.logger.info("Configuration validation passed successfully")
        return True
    
    def _validate_database_config(self, errors: List[str], warnings: List[str]):
        """Validate database configuration and permissions."""
        db_path = Path(self.database_path)
        
        if db_path.exists() and not db_path.is_file():
            errors.append(f"Database path exists but is not a file: {self.database_path}")
        
        # Check if we can create/write to the database directory
        db_dir = db_path.parent
        if not db_dir.exists():
            try:
                db_dir.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created database directory: {db_dir}")
            except PermissionError:
                errors.append(f"Cannot create database directory: {db_dir}")
            except Exception as e:
                errors.append(f"Error creating database directory {db_dir}: {e}")
        elif not os.access(db_dir, os.W_OK):
            errors.append(f"Cannot write to database directory: {db_dir}")
        
        # Check database file permissions if it exists
        if db_path.exists():
            if not os.access(db_path, os.R_OK | os.W_OK):
                errors.append(f"Cannot read/write database file: {self.database_path}")
            
            # Check file size
            try:
                file_size = db_path.stat().st_size
                if file_size > 100 * 1024 * 1024:  # 100MB
                    warnings.append(f"Large database file ({file_size / 1024 / 1024:.1f}MB) may impact performance")
            except OSError as e:
                warnings.append(f"Cannot check database file size: {e}")
        
        # Validate database integrity
        try:
            self.validate_database_integrity()
        except Exception as e:
            warnings.append(f"Database integrity check failed: {e}")
    
    def validate_database_integrity(self) -> bool:
        """Validate database integrity and required tables."""
        try:
            if not Path(self.database_path).exists():
                self.logger.info("Database does not exist, will be created on first run")
                return True
            
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Check if required tables exist
            required_tables = ['jobs', 'keywords', 'channels']
            existing_tables = []
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            for row in cursor.fetchall():
                existing_tables.append(row[0])
            
            missing_tables = [table for table in required_tables if table not in existing_tables]
            
            if missing_tables:
                self.logger.warning(f"Missing database tables: {missing_tables}. They will be created on first run.")
            
            conn.close()
            return True
            
        except Exception as e:
            self.logger.error(f"Database validation failed: {e}")
            return False
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration (without sensitive data)."""
        return {
            'target_channels_count': len(self.target_channels),
            'filter_keywords_count': len(self.filter_keywords),
            'output_method': self.output_method,
            'send_to_self': self.send_to_self,
            'target_entity_configured': bool(self.get_target_entity()),
            'date_filter_hours': self.date_filter_hours,
            'message_delay_range': f"{self.message_delay_min}-{self.message_delay_max}s",
            'database_path': self.database_path,
            'log_level': self.log_level,
            'web_enabled': self.web_port > 0,
            'scheduling_enabled': self.schedule_interval_minutes > 0,
            'batch_size': self.batch_size,
            'max_retries': self.max_retries
        }

# Global config instance
config = Config()