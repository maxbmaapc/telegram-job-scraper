import asyncio
import logging
import os
import re
from typing import List, Dict, Any, Optional
from telethon import TelegramClient, events
from telethon.tl.types import Channel, Chat, User
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, FloodWaitError
from telethon.sessions import StringSession

# Try to import config and logging_config with fallbacks
try:
    from .config import config
    from .logging_config import get_logger
except ImportError:
    # Fallback for when running outside package context
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    try:
        from config import config
        from logging_config import get_logger
    except ImportError:
        # Final fallback - create minimal versions
        class MinimalConfig:
            def __init__(self):
                self.api_id = os.getenv('API_ID')
                self.api_hash = os.getenv('API_HASH')
                self.phone_number = os.getenv('PHONE_NUMBER')
                self.target_channels = os.getenv('TARGET_CHANNELS', '').split(',') if os.getenv('TARGET_CHANNELS') else []
                self.session_name = 'telegram_job_scraper'
        
        config = MinimalConfig()
        
        def get_logger(name):
            logging.basicConfig(level=logging.INFO)
            return logging.getLogger(name)

logger = get_logger(__name__)

class TelegramJobClient:
    """Telegram client for job scraping with automatic phone code handling"""
    
    def __init__(self):
        if config.auth_method == 'bot':
            # Bot authentication
            self.client = TelegramClient(
                config.session_name,
                config.api_id,
                config.api_hash
            )
        else:
            # User authentication
            self.client = TelegramClient(
                config.session_name,
                config.api_id,
                config.api_hash
            )
        
        self.me = None
        self.target_entities = []
        
    async def start(self):
        """Start the Telegram client with automatic phone code handling"""
        try:
            if config.auth_method == 'bot':
                # Bot authentication
                await self.client.start(bot_token=config.bot_token)
                self.me = await self.client.get_me()
                logger.info(f'Bot logged in as {self.me.first_name} (@{self.me.username})')
            else:
                # Check for existing session first
                has_session = self._check_existing_session()
                if has_session:
                    logger.info('Attempting to use existing session file...')
                
                # Try to start with existing session first
                try:
                    await self.client.connect()
                    if await self.client.is_user_authorized():
                        self.me = await self.client.get_me()
                        logger.info(f'Successfully authenticated with existing session as {self.me.first_name} (@{self.me.username})')
                        await self._load_target_entities()
                        return
                    else:
                        logger.info('Existing session expired, requesting new authentication...')
                except Exception as e:
                    logger.info(f'Could not use existing session: {e}')
                
                # Request new code and authenticate
                await self._authenticate_with_new_code()
            
        except Exception as e:
            logger.error(f'Failed to start Telegram client: {e}')
            raise
    
    async def _authenticate_with_new_code(self):
        """Authenticate by requesting a new code and handling the process automatically"""
        try:
            logger.info('Requesting new authentication code from Telegram...')
            
            # Request the code
            await self.client.send_code_request(config.phone_number)
            logger.info('Authentication code requested successfully')
            
            # Wait a moment for the code to arrive
            logger.info('Waiting for code to arrive... (check your Telegram app/SMS)')
            await asyncio.sleep(5)  # Give some time for the code to arrive
            
            # Get the code from environment variable
            phone_code = self._get_phone_code()
            logger.info(f'Using phone code: {phone_code}')
            
            # Sign in with the code
            await self.client.sign_in(config.phone_number, phone_code)
            logger.info('Successfully signed in with phone code')
            
            # Get user info
            self.me = await self.client.get_me()
            logger.info(f'Logged in as {self.me.first_name} (@{self.me.username})')
            
            # Load target entities
            await self._load_target_entities()
            
        except FloodWaitError as e:
            wait_time = e.seconds
            logger.info(f'Telegram requires waiting {wait_time} seconds. Waiting automatically...')
            
            # Wait for the cooldown to expire
            for remaining in range(wait_time, 0, -1):
                if remaining % 10 == 0:  # Log every 10 seconds
                    logger.info(f'Waiting {remaining} seconds before retrying...')
                await asyncio.sleep(1)
            
            logger.info('Cooldown expired, retrying authentication...')
            # Retry the authentication
            await self._authenticate_with_new_code()
            
        except PhoneCodeInvalidError:
            logger.error('Invalid phone code provided. Check TELEGRAM_PHONE_CODE environment variable.')
            raise
        except SessionPasswordNeededError:
            logger.error('Two-factor authentication is enabled. Please disable it temporarily or provide the password via TELEGRAM_2FA_PASSWORD environment variable.')
            # Try to handle 2FA automatically
            try:
                password = self._get_2fa_password()
                await self.client.sign_in(password=password)
                self.me = await self.client.get_me()
                logger.info(f'Logged in with 2FA as {self.me.first_name} (@{self.me.username})')
                # Get target entities after successful 2FA
                await self._load_target_entities()
            except Exception as e:
                logger.error(f'Failed to handle 2FA: {e}')
                raise
        except Exception as e:
            logger.error(f'Failed to authenticate with new code: {e}')
            raise
    
    def _get_phone_code(self) -> str:
        """Get phone code from environment variable"""
        phone_code = os.getenv('TELEGRAM_PHONE_CODE')
        if phone_code:
            logger.info(f'Using phone code from environment variable: {phone_code}')
            return phone_code
        else:
            logger.error('TELEGRAM_PHONE_CODE environment variable not set')
            raise ValueError('TELEGRAM_PHONE_CODE environment variable is required for automatic authentication')
    
    def _get_2fa_password(self) -> str:
        """Get 2FA password from environment variable"""
        password = os.getenv('TELEGRAM_2FA_PASSWORD')
        if password:
            logger.info('Using 2FA password from environment variable')
            return password
        else:
            logger.error('TELEGRAM_2FA_PASSWORD environment variable not set')
            raise ValueError('TELEGRAM_2FA_PASSWORD environment variable is required for 2FA authentication')
    
    def _check_existing_session(self) -> bool:
        """Check if an existing session file exists"""
        session_file = f"{config.session_name}.session"
        if os.path.exists(session_file):
            file_size = os.path.getsize(session_file)
            logger.info(f'Found existing session file: {session_file} ({file_size} bytes)')
            return True
        else:
            logger.info(f'No existing session file found: {session_file}')
            return False
    
    async def _load_target_entities(self):
        """Load target channels/groups"""
        for channel_id in config.target_channels:
            try:
                # Try to get entity by ID
                entity = await self.client.get_entity(int(channel_id))
                self.target_entities.append(entity)
                logger.info(f'Loaded target entity: {getattr(entity, "title", "Unknown")} ({channel_id})')
            except ValueError:
                logger.warning(f'Invalid channel ID: {channel_id}')
            except Exception as e:
                logger.error(f'Failed to load entity {channel_id}: {e}')
    
    async def get_messages(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get messages from all target channels"""
        all_messages = []
        
        for entity in self.target_entities:
            try:
                messages = await self.client.get_messages(entity, limit=limit)
                
                for message in messages:
                    if message and message.text:
                        message_dict = {
                            'id': message.id,
                            'message': message.text,
                            'date': message.date,
                            'sender_id': message.sender_id,
                            'chat_id': message.chat_id,
                            'chat_title': getattr(entity, 'title', 'Unknown'),
                            'forward_from': getattr(message, 'forward_from', None),
                            'reply_to': message.reply_to,
                            'media': bool(message.media),
                            'views': getattr(message, 'views', None),
                            'forwards': getattr(message, 'forwards', None)
                        }
                        all_messages.append(message_dict)
                        
                logger.info(f'Retrieved {len(messages)} messages from {getattr(entity, "title", "Unknown")}')
                
            except Exception as e:
                logger.error(f'Failed to get messages from {getattr(entity, "title", "Unknown")}: {e}')
        
        return all_messages
    
    async def send_message_to_self(self, text: str):
        """Send a message to yourself"""
        try:
            await self.client.send_message(self.me, text)
            logger.info('Message sent to self')
        except Exception as e:
            logger.error(f'Failed to send message to self: {e}')
    
    async def send_message_to_target(self, text: str, target_entity: str):
        """Send a message to a target entity (user, channel, or group)"""
        try:
            # Try to resolve the target entity
            entity = await self._resolve_target_entity(target_entity)
            if entity:
                await self.client.send_message(entity, text)
                logger.info(f'Message sent to target: {getattr(entity, "title", getattr(entity, "first_name", "Unknown"))}')
            else:
                logger.error(f'Could not resolve target entity: {target_entity}')
        except Exception as e:
            logger.error(f'Failed to send message to target {target_entity}: {e}')
    
    async def _resolve_target_entity(self, target_entity: str):
        """Resolve a target entity from various formats"""
        try:
            # Try as user ID
            if target_entity.isdigit():
                return await self.client.get_entity(int(target_entity))
            
            # Try as username (with or without @)
            if target_entity.startswith('@'):
                target_entity = target_entity[1:]
            return await self.client.get_entity(target_entity)
            
        except ValueError:
            # Try as phone number
            try:
                return await self.client.get_entity(target_entity)
            except:
                pass
        
        except Exception as e:
            logger.error(f'Failed to resolve target entity {target_entity}: {e}')
        
        return None
    
    async def get_entity_info(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get information about an entity"""
        try:
            entity = await self.client.get_entity(int(entity_id))
            return {
                'id': entity.id,
                'title': getattr(entity, 'title', None),
                'username': getattr(entity, 'username', None),
                'participants_count': getattr(entity, 'participants_count', None),
                'type': type(entity).__name__
            }
        except Exception as e:
            logger.error(f'Failed to get entity info for {entity_id}: {e}')
            return None
    
    async def join_channel(self, channel_username: str) -> bool:
        """Join a channel by username"""
        try:
            from telethon.tl.functions.channels import JoinChannelRequest
            await self.client(JoinChannelRequest(channel_username))
            logger.info(f'Successfully joined channel: {channel_username}')
            return True
        except Exception as e:
            logger.error(f'Failed to join channel {channel_username}: {e}')
            return False
    
    async def disconnect(self):
        """Disconnect the client"""
        await self.client.disconnect()
        logger.info('Telegram client disconnected')

class MessageMonitor:
    """Monitor for real-time message updates"""
    
    def __init__(self, client: TelegramJobClient, filter_func):
        self.client = client
        self.filter_func = filter_func
        self.running = False
    
    async def start_monitoring(self):
        """Start monitoring for new messages"""
        self.running = True
        
        @self.client.client.on(events.NewMessage(chats=self.client.target_entities))
        async def handle_new_message(event):
            if not self.running:
                return
                
            try:
                message = {
                    'id': event.message.id,
                    'message': event.message.text,
                    'date': event.message.date,
                    'sender_id': event.message.sender_id,
                    'chat_id': event.message.chat_id,
                    'chat_title': getattr(event.chat, 'title', 'Unknown'),
                    'forward_from': getattr(event.message, 'forward_from', None),
                    'reply_to': event.message.reply_to,
                    'media': bool(event.message.media),
                    'views': getattr(event.message, 'views', None),
                    'forwards': getattr(event.message, 'forwards', None)
                }
                
                if self.filter_func(message):
                    logger.info(f'New matching message from {message["chat_title"]}')
                    # Handle the matching message
                    await self._handle_matching_message(message)
                    
            except Exception as e:
                logger.error(f'Error handling new message: {e}')
        
        logger.info('Started monitoring for new messages')
        
        # Keep the client running
        await self.client.client.run_until_disconnected()
    
    async def _handle_matching_message(self, message: Dict[str, Any]):
        """Handle a matching message"""
        # This will be implemented by the main application
        pass
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        logger.info('Stopped monitoring for new messages')