import os
import logging
import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

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
        self.logger = logging.getLogger(__name__)
        
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
        """Setup basic logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler()
            ]
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
        """Comprehensive configuration validation."""
        errors = []
        
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
        
        # Validate filter keywords
        if not self.filter_keywords:
            errors.append("No filter keywords configured. Set FILTER_KEYWORDS environment variable")
        
        # Validate date filter
        if self.date_filter_hours < 0:
            errors.append("DATE_FILTER_HOURS must be non-negative")
        
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
        
        # Validate database path
        if self.output_method == 'database':
            db_path = Path(self.database_path)
            if db_path.exists() and not db_path.is_file():
                errors.append(f"Database path exists but is not a file: {self.database_path}")
            
            # Check if we can create/write to the database directory
            db_dir = db_path.parent
            if not db_dir.exists():
                try:
                    db_dir.mkdir(parents=True, exist_ok=True)
                except PermissionError:
                    errors.append(f"Cannot create database directory: {db_dir}")
            elif not os.access(db_dir, os.W_OK):
                errors.append(f"Cannot write to database directory: {db_dir}")
        
        # Validate web UI settings
        if self.web_port < 1 or self.web_port > 65535:
            errors.append(f"Invalid web port: {self.web_port}. Must be between 1 and 65535")
        
        # Validate scheduling settings
        if self.schedule_interval_minutes < 1:
            errors.append("SCHEDULE_INTERVAL_MINUTES must be at least 1 minute")
        
        if self.schedule_start_time and self.schedule_end_time:
            try:
                from datetime import datetime
                datetime.strptime(self.schedule_start_time, '%H:%M')
                datetime.strptime(self.schedule_end_time, '%H:%M')
            except ValueError:
                errors.append("Schedule times must be in HH:MM format (e.g., 09:00)")
        
        # Validate performance settings
        if self.batch_size < 1:
            errors.append("BATCH_SIZE must be at least 1")
        
        if self.max_retries < 0:
            errors.append("MAX_RETRIES must be non-negative")
        
        # Raise exception if any errors found
        if errors:
            error_message = "Configuration validation failed:\n" + "\n".join(f"- {error}" for error in errors)
            raise ConfigValidationError(error_message)
        
        self.logger.info("Configuration validation passed successfully")
        return True
    
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