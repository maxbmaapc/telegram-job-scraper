import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class MessageFilter:
    """Filter class for Telegram messages"""
    
    def __init__(self, keywords: List[str], date_filter_hours: int = 24):
        self.keywords = [keyword.lower() for keyword in keywords]
        self.date_filter_hours = date_filter_hours
        
    def matches_keywords(self, text: str) -> bool:
        """Check if text matches any of the configured keywords"""
        if not text:
            return False
            
        text_lower = text.lower()
        
        for keyword in self.keywords:
            if keyword in text_lower:
                logger.debug(f'Keyword match found: {keyword} in message')
                return True
        
        return False
    
    def matches_date_filter(self, message_date: datetime) -> bool:
        """Check if message is within the configured time window"""
        if self.date_filter_hours <= 0:
            return True  # No date filter
            
        cutoff_time = datetime.now() - timedelta(hours=self.date_filter_hours)
        return message_date >= cutoff_time
    
    def filter_message(self, message: Dict[str, Any]) -> bool:
        """Apply all filters to a message"""
        try:
            # Extract message text
            text = self._extract_message_text(message)
            if not text:
                return False
            
            # Check keyword filter
            if not self.matches_keywords(text):
                return False
            
            # Check date filter
            message_date = self._extract_message_date(message)
            if not self.matches_date_filter(message_date):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f'Error filtering message: {e}')
            return False
    
    def _extract_message_text(self, message: Dict[str, Any]) -> str:
        """Extract text content from message"""
        # Handle different message types
        if 'message' in message:
            return message['message'] or ''
        elif 'text' in message:
            return message['text'] or ''
        elif 'caption' in message:
            return message['caption'] or ''
        
        return ''
    
    def _extract_message_date(self, message: Dict[str, Any]) -> datetime:
        """Extract date from message"""
        # Handle different date fields
        if 'date' in message:
            return message['date']
        elif 'message_date' in message:
            return message['message_date']
        
        # Default to current time if no date found
        return datetime.now()
    
    def get_matched_keywords(self, text: str) -> List[str]:
        """Get list of keywords that matched in the text"""
        if not text:
            return []
            
        text_lower = text.lower()
        matched = []
        
        for keyword in self.keywords:
            if keyword in text_lower:
                matched.append(keyword)
        
        return matched

class AdvancedFilter(MessageFilter):
    """Advanced filter with additional capabilities"""
    
    def __init__(self, keywords: List[str], date_filter_hours: int = 24, 
                 exclude_keywords: List[str] = None, 
                 min_salary: Optional[int] = None,
                 max_salary: Optional[int] = None):
        super().__init__(keywords, date_filter_hours)
        self.exclude_keywords = [kw.lower() for kw in (exclude_keywords or [])]
        self.min_salary = min_salary
        self.max_salary = max_salary
    
    def filter_message(self, message: Dict[str, Any]) -> bool:
        """Apply advanced filters to a message"""
        # First apply basic filters
        if not super().filter_message(message):
            return False
        
        text = self._extract_message_text(message)
        text_lower = text.lower()
        
        # Check exclude keywords
        for exclude_keyword in self.exclude_keywords:
            if exclude_keyword in text_lower:
                logger.debug(f'Excluded due to keyword: {exclude_keyword}')
                return False
        
        # Check salary range (if configured)
        if self.min_salary or self.max_salary:
            if not self._matches_salary_range(text):
                return False
        
        return True
    
    def _matches_salary_range(self, text: str) -> bool:
        """Check if message contains salary within specified range"""
        # Simple salary extraction (can be enhanced)
        salary_patterns = [
            r'£(\d{1,3}(?:,\d{3})*(?:\s*k)?)',  # £50k, £50,000
            r'\$(\d{1,3}(?:,\d{3})*(?:\s*k)?)',  # $50k, $50,000
            r'(\d{1,3}(?:,\d{3})*(?:\s*k)?)\s*(?:pounds?|gbp)',  # 50k pounds
        ]
        
        for pattern in salary_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    # Convert to number
                    salary_str = match.replace(',', '').replace('k', '000')
                    salary = int(salary_str)
                    
                    # Check range
                    if self.min_salary and salary < self.min_salary:
                        continue
                    if self.max_salary and salary > self.max_salary:
                        continue
                    
                    return True
                except ValueError:
                    continue
        
        return not (self.min_salary or self.max_salary)  # If no salary filter, pass