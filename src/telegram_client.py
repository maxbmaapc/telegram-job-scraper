import asyncio
import logging
from typing import List, Dict, Any, Optional
from telethon import TelegramClient, events
from telethon.tl.types import Channel, Chat, User
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from telethon.sessions import StringSession

from .config import config

logger = logging.getLogger(__name__)

class TelegramJobClient:
    """Telegram client for job scraping"""
    
    def __init__(self):
        if config.auth_method == 'bot':
            # Bot authentication
            self.client = TelegramClient(
                config.session_name,
                config.api_id,
                config.api_hash
            ).start(bot_token=config.bot_token)
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
        """Start the Telegram client"""
        try:
            if config.auth_method == 'bot':
                # Bot authentication - already started in __init__
                await self.client.connect()
                self.me = await self.client.get_me()
                logger.info(f'Bot logged in as {self.me.first_name} (@{self.me.username})')
            else:
                # User authentication
                await self.client.start(phone=config.phone_number)
                self.me = await self.client.get_me()
                logger.info(f'Logged in as {self.me.first_name} (@{self.me.username})')
            
            # Get target entities
            await self._load_target_entities()
            
        except SessionPasswordNeededError:
            logger.error('Two-factor authentication is enabled. Please disable it temporarily or use a different account.')
            raise
        except PhoneCodeInvalidError:
            logger.error('Invalid phone code. Please check your code and try again.')
            raise
        except Exception as e:
            logger.error(f'Failed to start Telegram client: {e}')
            raise
    
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