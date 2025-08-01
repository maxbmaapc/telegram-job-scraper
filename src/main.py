#!/usr/bin/env python3
"""
Telegram Job Scraper - Main Entry Point

This script monitors Telegram channels/groups for job postings that match
specific keywords and filters, then outputs them via various methods.
"""

import asyncio
import argparse
import logging
import sys
from typing import List, Dict, Any

from .config import config
from .telegram_client import TelegramJobClient, MessageMonitor
from .filters import MessageFilter, AdvancedFilter
from .output import OutputManager, DatabaseManager
from .scheduler import JobScheduler, create_scheduler_from_config
from .utils import calculate_message_stats, safe_json_dump

logger = logging.getLogger(__name__)

class JobScraper:
    """Main job scraper class"""
    
    def __init__(self):
        self.telegram_client = None
        self.message_filter = None
        self.output_manager = None
        self.database_manager = None
        
    async def initialize(self):
        """Initialize all components"""
        try:
            # Validate configuration
            if not config.validate():
                logger.error("Configuration validation failed")
                return False
            
            # Initialize Telegram client
            self.telegram_client = TelegramJobClient()
            await self.telegram_client.start()
            
            # Initialize message filter
            self.message_filter = MessageFilter(
                keywords=config.filter_keywords,
                date_filter_hours=config.date_filter_hours
            )
            
            # Initialize output manager
            self.output_manager = OutputManager(config.output_method)
            if config.output_method == 'telegram':
                self.output_manager.set_telegram_client(self.telegram_client)
            
            # Initialize database manager
            self.database_manager = DatabaseManager()
            
            logger.info("Job scraper initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize job scraper: {e}")
            return False
    
    async def scrape_jobs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Scrape jobs from configured channels"""
        try:
            logger.info(f"Starting job scraping from {len(config.target_channels)} channels")
            
            # Get messages from all channels
            messages = await self.telegram_client.get_messages(limit=limit)
            logger.info(f"Retrieved {len(messages)} messages")
            
            # Filter messages
            filtered_jobs = []
            for message in messages:
                if self.message_filter.filter_message(message):
                    # Add matched keywords to the message
                    text = self.message_filter._extract_message_text(message)
                    message['matched_keywords'] = self.message_filter.get_matched_keywords(text)
                    filtered_jobs.append(message)
            
            logger.info(f"Found {len(filtered_jobs)} matching job postings")
            
            # Calculate and log statistics
            stats = calculate_message_stats(messages)
            logger.info(f"Message statistics: {stats}")
            
            return filtered_jobs
            
        except Exception as e:
            logger.error(f"Error during job scraping: {e}")
            return []
    
    async def output_jobs(self, jobs: List[Dict[str, Any]]):
        """Output filtered jobs"""
        if not jobs:
            logger.info("No jobs to output")
            return
        
        try:
            await self.output_manager.output_jobs(jobs)
            logger.info(f"Successfully output {len(jobs)} jobs")
        except Exception as e:
            logger.error(f"Error outputting jobs: {e}")
    
    async def run_single_scrape(self, limit: int = 100):
        """Run a single scraping session"""
        logger.info("Starting single scraping session")
        
        # Scrape jobs
        jobs = await self.scrape_jobs(limit)
        
        # Output jobs
        await self.output_jobs(jobs)
        
        logger.info("Single scraping session completed")
    
    async def run_continuous_monitoring(self):
        """Run continuous monitoring for new messages"""
        logger.info("Starting continuous monitoring")
        
        # Create message monitor
        monitor = MessageMonitor(self.telegram_client, self.message_filter.filter_message)
        
        # Override the message handler
        async def handle_matching_message(message: Dict[str, Any]):
            """Handle a matching message in real-time"""
            text = self.message_filter._extract_message_text(message)
            message['matched_keywords'] = self.message_filter.get_matched_keywords(text)
            
            logger.info(f"New matching job found: {message.get('chat_title', 'Unknown')}")
            
            # Output the single job
            await self.output_jobs([message])
        
        monitor._handle_matching_message = handle_matching_message
        
        # Start monitoring
        await monitor.start_monitoring()
    
    async def run_scheduled_scraping(self):
        """Run scheduled scraping at specified intervals"""
        logger.info("Starting scheduled scraping")
        
        # Create scheduler
        scheduler = create_scheduler_from_config(
            interval_minutes=config.schedule_interval_minutes,
            start_time=config.schedule_start_time,
            end_time=config.schedule_end_time,
            days_of_week=config.schedule_days_of_week,
            max_runs_per_day=config.schedule_max_runs_per_day
        )
        
        # Define the job function
        async def scheduled_job():
            """Job function to run on schedule"""
            try:
                jobs = await self.scrape_jobs(limit=100)
                await self.output_jobs(jobs)
            except Exception as e:
                logger.error(f"Error in scheduled job: {e}")
        
        # Start the scheduler
        await scheduler.run_scheduled(scheduled_job)
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.telegram_client:
            await self.telegram_client.disconnect()
        logger.info("Cleanup completed")

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Telegram Job Scraper')
    parser.add_argument('--mode', choices=['single', 'continuous', 'scheduled'], default='single',
                       help='Scraping mode: single run, continuous monitoring, or scheduled (default: single)')
    parser.add_argument('--limit', type=int, default=100,
                       help='Number of messages to retrieve per channel')
    parser.add_argument('--config', type=str,
                       help='Path to custom configuration file')
    
    args = parser.parse_args()
    
    # Create scraper instance
    scraper = JobScraper()
    
    try:
        # Initialize scraper
        if not await scraper.initialize():
            logger.error("Failed to initialize scraper")
            sys.exit(1)
        
        # Run based on mode
        if args.mode == 'single':
            await scraper.run_single_scrape(args.limit)
        elif args.mode == 'continuous':
            await scraper.run_continuous_monitoring()
        elif args.mode == 'scheduled':
            await scraper.run_scheduled_scraping()
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        await scraper.cleanup()

def run():
    """Entry point for package execution"""
    asyncio.run(main())

if __name__ == '__main__':
    run()