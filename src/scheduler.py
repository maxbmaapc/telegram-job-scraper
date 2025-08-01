import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Optional, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ScheduleConfig:
    """Configuration for scheduling"""
    interval_minutes: int = 30  # Default: every 30 minutes
    start_time: Optional[str] = None  # e.g., "09:00"
    end_time: Optional[str] = None    # e.g., "18:00"
    days_of_week: list = None  # e.g., [0,1,2,3,4] for Mon-Fri
    max_runs_per_day: Optional[int] = None

class JobScheduler:
    """Scheduler for running jobs at specified intervals"""
    
    def __init__(self, config: ScheduleConfig):
        self.config = config
        self.running = False
        self.last_run = None
        self.runs_today = 0
        self.last_run_date = None
    
    def _parse_time(self, time_str: str) -> tuple:
        """Parse time string (HH:MM) to hours and minutes"""
        if not time_str:
            return None, None
        try:
            hours, minutes = map(int, time_str.split(':'))
            return hours, minutes
        except ValueError:
            logger.error(f"Invalid time format: {time_str}. Use HH:MM format.")
            return None, None
    
    def _is_within_time_window(self) -> bool:
        """Check if current time is within the allowed window"""
        now = datetime.now()
        
        # Check start time
        if self.config.start_time:
            start_hours, start_minutes = self._parse_time(self.config.start_time)
            if start_hours is not None:
                start_time = now.replace(hour=start_hours, minute=start_minutes, second=0, microsecond=0)
                if now < start_time:
                    return False
        
        # Check end time
        if self.config.end_time:
            end_hours, end_minutes = self._parse_time(self.config.end_time)
            if end_hours is not None:
                end_time = now.replace(hour=end_hours, minute=end_minutes, second=0, microsecond=0)
                if now > end_time:
                    return False
        
        return True
    
    def _is_allowed_day(self) -> bool:
        """Check if current day is allowed"""
        if not self.config.days_of_week:
            return True
        
        current_day = datetime.now().weekday()  # 0=Monday, 6=Sunday
        return current_day in self.config.days_of_week
    
    def _can_run_today(self) -> bool:
        """Check if we can run today based on max_runs_per_day"""
        if not self.config.max_runs_per_day:
            return True
        
        today = datetime.now().date()
        if self.last_run_date != today:
            self.runs_today = 0
            self.last_run_date = today
        
        return self.runs_today < self.config.max_runs_per_day
    
    def _should_run_now(self) -> bool:
        """Determine if the job should run now"""
        # Check if within time window
        if not self._is_within_time_window():
            return False
        
        # Check if allowed day
        if not self._is_allowed_day():
            return False
        
        # Check if can run today
        if not self._can_run_today():
            return False
        
        # Check if enough time has passed since last run
        if self.last_run:
            time_since_last = datetime.now() - self.last_run
            if time_since_last.total_seconds() < self.config.interval_minutes * 60:
                return False
        
        return True
    
    async def run_scheduled(self, job_function: Callable):
        """Run the job function on schedule"""
        self.running = True
        logger.info(f"Scheduler started with interval: {self.config.interval_minutes} minutes")
        
        while self.running:
            try:
                if self._should_run_now():
                    logger.info("Running scheduled job...")
                    
                    # Run the job
                    await job_function()
                    
                    # Update run statistics
                    self.last_run = datetime.now()
                    self.runs_today += 1
                    
                    logger.info(f"Job completed. Runs today: {self.runs_today}")
                    
                    # Wait for next interval
                    await asyncio.sleep(self.config.interval_minutes * 60)
                else:
                    # Wait a bit before checking again
                    await asyncio.sleep(60)  # Check every minute
                    
            except Exception as e:
                logger.error(f"Error in scheduled job: {e}")
                # Wait before retrying
                await asyncio.sleep(300)  # 5 minutes
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        logger.info("Scheduler stopped")

def create_scheduler_from_config(interval_minutes: int = 30,
                                start_time: Optional[str] = None,
                                end_time: Optional[str] = None,
                                days_of_week: Optional[list] = None,
                                max_runs_per_day: Optional[int] = None) -> JobScheduler:
    """Create a scheduler from configuration parameters"""
    
    config = ScheduleConfig(
        interval_minutes=interval_minutes,
        start_time=start_time,
        end_time=end_time,
        days_of_week=days_of_week or [0, 1, 2, 3, 4, 5, 6],  # All days by default
        max_runs_per_day=max_runs_per_day
    )
    
    return JobScheduler(config)

# Example usage:
# scheduler = create_scheduler_from_config(
#     interval_minutes=30,
#     start_time="09:00",
#     end_time="18:00",
#     days_of_week=[0, 1, 2, 3, 4],  # Mon-Fri
#     max_runs_per_day=10
# )
# await scheduler.run_scheduled(your_job_function)