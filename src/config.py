import os
import logging
from dotenv import load_dotenv
from typing import List, Optional

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the Telegram Job Scraper"""
    
    def __init__(self):
        # Telegram API Credentials
        self.api_id = self._get_required_env('API_ID')
        self.api_hash = self._get_required_env('API_HASH')
        self.phone_number = self._get_required_env('PHONE_NUMBER')
        
        # Target Channels
        self.target_channels = self._parse_list_env('TARGET_CHANNELS')
        
        # Filter Settings
        self.filter_keywords = self._parse_list_env('FILTER_KEYWORDS')
        self.date_filter_hours = int(os.getenv('DATE_FILTER_HOURS', '24'))
        
        # Output Settings
        self.output_method = os.getenv('OUTPUT_METHOD', 'telegram').lower()
        self.send_to_self = os.getenv('SEND_TO_SELF', 'true').lower() == 'true'
        
        # Database Settings
        self.database_path = os.getenv('DATABASE_PATH', 'jobs.db')
        
        # Logging
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        
        # Web UI Settings
        self.web_host = os.getenv('WEB_HOST', 'localhost')
        self.web_port = int(os.getenv('WEB_PORT', '5000'))
        
        # Session file
        self.session_name = 'telegram_job_scraper'
        
        # Setup logging
        self._setup_logging()
    
    def _get_required_env(self, key: str) -> str:
        """Get a required environment variable"""
        value = os.getenv(key)
        if not value:
            raise ValueError(f'Required environment variable {key} is not set')
        return value
    
    def _parse_list_env(self, key: str) -> List[str]:
        """Parse a comma-separated environment variable into a list"""
        value = os.getenv(key, '')
        if not value:
            return []
        return [item.strip() for item in value.split(',') if item.strip()]
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, self.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('telegram_scraper.log'),
                logging.StreamHandler()
            ]
        )
    
    def validate(self) -> bool:
        """Validate configuration"""
        if not self.target_channels:
            logging.warning('No target channels configured')
            return False
        
        if not self.filter_keywords:
            logging.warning('No filter keywords configured')
            return False
        
        return True

# Global config instance
config = Config()