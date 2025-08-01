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
  python run.py --limit 50         # Scrape 50 messages per channel
  python run.py --help             # Show this help message
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['single', 'continuous'],
        default='single',
        help='Scraping mode: single run or continuous monitoring (default: single)'
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