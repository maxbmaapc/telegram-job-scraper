#!/usr/bin/env python3
"""
Simple runner script for Telegram Job Scraper

This script provides an easy way to run the job scraper with different modes
and configurations.
"""

import sys
import os
import argparse

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import main as scraper_main

def main():
    """Main entry point for the runner script"""
    parser = argparse.ArgumentParser(
        description='Telegram Job Scraper Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                    # Run single scrape with default settings
  python run.py --mode continuous  # Run continuous monitoring
  python run.py --mode scheduled   # Run scheduled scraping (every 30 min by default)
  python run.py --limit 50         # Scrape 50 messages per channel
  python run.py --help             # Show this help message

Scheduling Examples:
  # Run every 15 minutes during business hours
  SCHEDULE_INTERVAL_MINUTES=15 SCHEDULE_START_TIME=09:00 SCHEDULE_END_TIME=18:00 python run.py --mode scheduled
  
  # Run every hour, weekdays only
  SCHEDULE_INTERVAL_MINUTES=60 SCHEDULE_DAYS_OF_WEEK=0,1,2,3,4 python run.py --mode scheduled
  
  # Run every 30 minutes, max 5 times per day
  SCHEDULE_INTERVAL_MINUTES=30 SCHEDULE_MAX_RUNS_PER_DAY=5 python run.py --mode scheduled
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['single', 'continuous', 'scheduled'],
        default='single',
        help='Scraping mode: single run, continuous monitoring, or scheduled (default: single)'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=100,
        help='Number of messages to retrieve per channel (default: 100)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to custom configuration file'
    )
    
    args = parser.parse_args()
    
    # Set up sys.argv for the main scraper
    sys.argv = ['main.py']
    if args.mode:
        sys.argv.extend(['--mode', args.mode])
    if args.limit:
        sys.argv.extend(['--limit', str(args.limit)])
    if args.config:
        sys.argv.extend(['--config', args.config])
    
    # Run the scraper
    import asyncio
    asyncio.run(scraper_main())

if __name__ == '__main__':
    main()