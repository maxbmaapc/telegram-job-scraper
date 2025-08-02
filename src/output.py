import json
import csv
import sqlite3
import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from .config import config

logger = logging.getLogger(__name__)

class OutputManager:
    """Manages different output methods for job postings"""
    
    def __init__(self, output_method: str = 'telegram'):
        self.output_method = output_method
        self.telegram_client = None
        
    def set_telegram_client(self, client):
        """Set the Telegram client for sending messages"""
        self.telegram_client = client
    
    async def output_jobs(self, jobs: List[Dict[str, Any]]):
        """Output jobs using the configured method"""
        if not jobs:
            logger.info('No jobs to output')
            return
        
        logger.info(f'Outputting {len(jobs)} jobs using {self.output_method} method')
        
        if self.output_method == 'telegram':
            await self._output_to_telegram(jobs)
        elif self.output_method == 'file':
            self._output_to_file(jobs)
        elif self.output_method == 'database':
            self._output_to_database(jobs)
        else:
            logger.error(f'Unknown output method: {self.output_method}')
    
    async def _output_to_telegram(self, jobs: List[Dict[str, Any]]):
        """Send jobs to Telegram"""
        if not self.telegram_client:
            logger.error('Telegram client not set')
            return
        
        for job in jobs:
            try:
                # Try to forward the original message first
                if await self._forward_original_message(job):
                    # If forwarding succeeded, send a brief summary
                    summary = self._format_job_summary(job)
                    if config.send_to_self:
                        await self.telegram_client.send_message_to_self(summary)
                    else:
                        target_entity = config.get_target_entity()
                        if target_entity:
                            await self.telegram_client.send_message_to_target(summary, target_entity)
                else:
                    # If forwarding failed, send the full formatted message
                    message = self._format_job_message(job)
                    if config.send_to_self:
                        await self.telegram_client.send_message_to_self(message)
                    else:
                        target_entity = config.get_target_entity()
                        if target_entity:
                            await self.telegram_client.send_message_to_target(message, target_entity)
                
                # Add delay to avoid rate limiting (Telegram has strict limits)
                # Use configurable delay to be safe and avoid bans
                import random
                delay = random.uniform(config.message_delay_min, config.message_delay_max)
                logger.debug(f'Waiting {delay:.1f}s before next message to avoid rate limiting')
                await asyncio.sleep(delay)
                
            except Exception as e:
                logger.error(f'Failed to send job to Telegram: {e}')
    
    async def _forward_original_message(self, job: Dict[str, Any]) -> bool:
        """Try to forward the original message"""
        try:
            # Get the original message from the channel
            original_message = await self.telegram_client.client.get_messages(
                job['chat_id'], 
                ids=job['id']
            )
            
            if original_message:
                # Forward the message to target
                if config.send_to_self:
                    await original_message.forward_to(self.telegram_client.me)
                else:
                    target_entity = config.get_target_entity()
                    if target_entity:
                        entity = await self.telegram_client._resolve_target_entity(target_entity)
                        if entity:
                            await original_message.forward_to(entity)
                            return True
                
                return True
        except Exception as e:
            logger.debug(f'Could not forward message: {e}')
            return False
        
        return False
    
    def _format_job_summary(self, job: Dict[str, Any]) -> str:
        """Format a brief summary for forwarded messages"""
        message = f"🔍 **Job Posting Forwarded**\n\n"
        
        # Add experience info if available
        if hasattr(self, 'message_filter') and hasattr(self.message_filter, 'get_experience_info'):
            text = job.get('message', '')
            experience_info = self.message_filter.get_experience_info(text)
            if experience_info:
                if experience_info.get('is_junior'):
                    message += f"👶 **Level:** Junior/Entry Level\n"
                elif experience_info.get('experience_years'):
                    message += f"⏰ **Experience:** {experience_info['experience_years']} years\n"
                
                # Add remote work info
                if experience_info.get('is_remote'):
                    message += f"🏠 **Work Type:** Remote\n"
        
        message += f"📢 **Channel:** {job['chat_title']}"
        
        if job.get('matched_keywords'):
            message += f"\n🏷️ **Keywords:** {', '.join(job['matched_keywords'])}"
        
        return message
    
    def _output_to_file(self, jobs: List[Dict[str, Any]]):
        """Save jobs to file (JSON or CSV)"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save as JSON
        json_file = f'jobs_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, indent=2, default=str)
        logger.info(f'Jobs saved to {json_file}')
        
        # Save as CSV
        csv_file = f'jobs_{timestamp}.csv'
        if jobs:
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=jobs[0].keys())
                writer.writeheader()
                writer.writerows(jobs)
            logger.info(f'Jobs saved to {csv_file}')
    
    def _output_to_database(self, jobs: List[Dict[str, Any]]):
        """Save jobs to SQLite database"""
        try:
            conn = sqlite3.connect(config.database_path)
            cursor = conn.cursor()
            
            # Create table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE,
                    message TEXT,
                    date TEXT,
                    sender_id INTEGER,
                    chat_id INTEGER,
                    chat_title TEXT,
                    matched_keywords TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert jobs
            for job in jobs:
                cursor.execute('''
                    INSERT OR IGNORE INTO jobs 
                    (telegram_id, message, date, sender_id, chat_id, chat_title, matched_keywords)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    job['id'],
                    job['message'],
                    job['date'].isoformat() if hasattr(job['date'], 'isoformat') else str(job['date']),
                    job['sender_id'],
                    job['chat_id'],
                    job['chat_title'],
                    json.dumps(job.get('matched_keywords', []))
                ))
            
            conn.commit()
            conn.close()
            logger.info(f'Jobs saved to database: {config.database_path}')
            
        except Exception as e:
            logger.error(f'Failed to save jobs to database: {e}')
    
    def _format_job_message(self, job: Dict[str, Any]) -> str:
        """Format a job posting for Telegram"""
        message = f"🔍 **Job Posting Found!**\n\n"
        
        # Add experience info if available
        if hasattr(self, 'message_filter') and hasattr(self.message_filter, 'get_experience_info'):
            text = job.get('message', '')
            experience_info = self.message_filter.get_experience_info(text)
            if experience_info:
                if experience_info.get('is_junior'):
                    message += f"👶 **Level:** Junior/Entry Level\n"
                elif experience_info.get('experience_years'):
                    message += f"⏰ **Experience:** {experience_info['experience_years']} years\n"
                else:
                    message += f"⏰ **Experience:** Not specified\n"
                
                # Add remote work info
                if experience_info.get('is_remote'):
                    message += f"🏠 **Work Type:** Remote\n"
        
        # Add message preview
        message += f"📝 **Preview:**\n{job['message'][:300]}"
        if len(job['message']) > 300:
            message += "..."
        
        message += f"\n\n📅 **Date:** {job['date']}"
        message += f"\n📢 **Channel:** {job['chat_title']}"
        
        if job.get('matched_keywords'):
            message += f"\n🏷️ **Matched Keywords:** {', '.join(job['matched_keywords'])}"
        
        # Add link to original message if possible
        if job.get('chat_id') and job.get('id'):
            # Try to create a link to the original message
            try:
                # For public channels, we can create a link
                if str(job['chat_id']).startswith('-100'):
                    channel_id = str(job['chat_id'])[4:]  # Remove -100 prefix
                    message_link = f"https://t.me/c/{channel_id}/{job['id']}"
                    message += f"\n🔗 **Original Post:** {message_link}"
            except:
                pass
        
        if job.get('views'):
            message += f"\n👁️ **Views:** {job['views']}"
        
        return message

class DatabaseManager:
    """Manages database operations"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.database_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create jobs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE,
                    message TEXT,
                    date TEXT,
                    sender_id INTEGER,
                    chat_id INTEGER,
                    chat_title TEXT,
                    matched_keywords TEXT,
                    favorite BOOLEAN DEFAULT FALSE,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create keywords table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS keywords (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    keyword TEXT UNIQUE,
                    active BOOLEAN DEFAULT TRUE,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create channels table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_id INTEGER UNIQUE,
                    title TEXT,
                    username TEXT,
                    active BOOLEAN DEFAULT TRUE,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info(f'Database initialized: {self.db_path}')
            
        except Exception as e:
            logger.error(f'Failed to initialize database: {e}')
    
    def get_jobs(self, limit: int = 100, favorite_only: bool = False) -> List[Dict[str, Any]]:
        """Get jobs from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = 'SELECT * FROM jobs'
            params = []
            
            if favorite_only:
                query += ' WHERE favorite = TRUE'
            
            query += ' ORDER BY created_at DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            columns = [description[0] for description in cursor.description]
            jobs = []
            for row in rows:
                job = dict(zip(columns, row))
                # Parse matched_keywords JSON
                if job['matched_keywords']:
                    try:
                        job['matched_keywords'] = json.loads(job['matched_keywords'])
                    except:
                        job['matched_keywords'] = []
                jobs.append(job)
            
            conn.close()
            return jobs
            
        except Exception as e:
            logger.error(f'Failed to get jobs from database: {e}')
            return []
    
    def toggle_favorite(self, job_id: int) -> bool:
        """Toggle favorite status of a job"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('UPDATE jobs SET favorite = NOT favorite WHERE id = ?', (job_id,))
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f'Failed to toggle favorite: {e}')
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total jobs
            cursor.execute('SELECT COUNT(*) FROM jobs')
            total_jobs = cursor.fetchone()[0]
            
            # Favorite jobs
            cursor.execute('SELECT COUNT(*) FROM jobs WHERE favorite = TRUE')
            favorite_jobs = cursor.fetchone()[0]
            
            # Jobs today
            cursor.execute('SELECT COUNT(*) FROM jobs WHERE DATE(created_at) = DATE(\'now\')')
            jobs_today = cursor.fetchone()[0]
            
            # Most active channels
            cursor.execute('''
                SELECT chat_title, COUNT(*) as count 
                FROM jobs 
                GROUP BY chat_title 
                ORDER BY count DESC 
                LIMIT 5
            ''')
            top_channels = cursor.fetchall()
            
            conn.close()
            
            return {
                'total_jobs': total_jobs,
                'favorite_jobs': favorite_jobs,
                'jobs_today': jobs_today,
                'top_channels': [{'title': title, 'count': count} for title, count in top_channels]
            }
            
        except Exception as e:
            logger.error(f'Failed to get statistics: {e}')
            return {}