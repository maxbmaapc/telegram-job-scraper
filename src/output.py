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
                message = self._format_job_message(job)
                
                # Determine where to send the message
                if config.send_to_self:
                    # Send to self (original behavior)
                    await self.telegram_client.send_message_to_self(message)
                else:
                    # Send to target entity
                    target_entity = config.get_target_entity()
                    if target_entity:
                        await self.telegram_client.send_message_to_target(message, target_entity)
                    else:
                        logger.error('No target entity configured for sending messages')
                        return
                
                # Add delay to avoid rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f'Failed to send job to Telegram: {e}')
    
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
        message += f"📝 **Message:**\n{job['message'][:500]}"
        if len(job['message']) > 500:
            message += "..."
        
        message += f"\n\n📅 **Date:** {job['date']}"
        message += f"\n📢 **Channel:** {job['chat_title']}"
        
        if job.get('matched_keywords'):
            message += f"\n🏷️ **Matched Keywords:** {', '.join(job['matched_keywords'])}"
        
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