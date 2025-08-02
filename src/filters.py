import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class RussianJobFilter:
    """Advanced filter for Russian job postings with specific requirements"""
    
    def __init__(self, keywords: List[str], date_filter_hours: int = 24):
        self.keywords = [keyword.lower() for keyword in keywords]
        self.date_filter_hours = date_filter_hours
        
        # Keywords to exclude (senior/middle positions)
        self.exclude_keywords = [
            'senior', 'сеньор', 'сениор', 'senior developer', 'сеньор разработчик',
            'middle', 'мидл', 'middle developer', 'мидл разработчик',
            'lead', 'лид', 'lead developer', 'лид разработчик',
            'team lead', 'тимлид', 'team leader',
            'architect', 'архитектор', 'software architect',
            'principal', 'принципал', 'principal developer',
            'staff', 'staff engineer', 'staff разработчик'
        ]
        
        # Junior keywords (if present, skip experience check)
        self.junior_keywords = [
            'junior', 'джуниор', 'джуниор разработчик', 'junior developer',
            'стажер', 'intern', 'internship', 'стажировка',
            'trainee', 'трени', 'trainee developer',
            'entry level', 'entry-level', 'начальный уровень',
            'без опыта', 'no experience', 'опыт не требуется'
        ]
        
        # Remote work keywords (required for job to be accepted)
        self.remote_keywords = [
            'remote', 'удаленка', 'удаленная работа', 'удаленно',
            'удалённо',
            'work from home', 'wfh', 'home office',
            'дистанционно', 'дистанционная работа',
            'онлайн', 'online', 'виртуально', 'virtual',
            'гибрид', 'hybrid', 'гибридная работа'
        ]
        
        # Experience patterns to check (in years)
        self.experience_patterns = [
            r'опыт\s*работы\s*(\d+)\s*(?:лет|года|год)',  # опыт работы 2 года
            r'(\d+)\s*(?:лет|года|год)\s*опыта',  # 2 года опыта
            r'опыт\s*от\s*(\d+)\s*(?:лет|года|год)',  # опыт от 2 лет
            r'опыт\s*до\s*(\d+)\s*(?:лет|года|год)',  # опыт до 2 лет
            r'(\d+)\+?\s*(?:лет|года|год)',  # 2+ лет
            r'experience\s*(\d+)\s*years?',  # experience 2 years
            r'(\d+)\s*years?\s*experience',  # 2 years experience
        ]
        
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
            
            # Check exclude keywords (senior/middle positions)
            if self.has_exclude_keywords(text):
                logger.debug(f'Excluded due to senior/middle keywords')
                return False
            
            # Check experience requirements
            if not self.matches_experience_requirements(text):
                logger.debug(f'Excluded due to experience requirements')
                return False
            
            # Check remote work requirement
            if not self.matches_remote_requirement(text):
                logger.debug(f'Excluded due to no remote work mentioned')
                return False
            
            return True
            
        except Exception as e:
            logger.error(f'Error filtering message: {e}')
            return False
    
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
    
    def has_exclude_keywords(self, text: str) -> bool:
        """Check if text contains exclude keywords (senior/middle positions)"""
        if not text:
            return False
            
        text_lower = text.lower()
        
        for exclude_keyword in self.exclude_keywords:
            if exclude_keyword in text_lower:
                return True
        
        return False
    
    def matches_experience_requirements(self, text: str) -> bool:
        """Check if message matches experience requirements"""
        if not text:
            return False
            
        text_lower = text.lower()
        
        # If junior keywords are present, accept the post
        for junior_keyword in self.junior_keywords:
            if junior_keyword in text_lower:
                return True
        
        # Check experience patterns
        for pattern in self.experience_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                try:
                    years = int(match)
                    # Accept if experience is 2 years or less
                    if years <= 2:
                        return True
                    else:
                        logger.debug(f'Experience too high: {years} years')
                        return False
                except ValueError:
                    continue
        
        # If no experience mentioned and no junior keywords, accept (could be entry level)
        return True
    
    def matches_remote_requirement(self, text: str) -> bool:
        """Check if message mentions remote work"""
        if not text:
            return False
            
        text_lower = text.lower()
        
        # Check for remote work keywords
        for remote_keyword in self.remote_keywords:
            if remote_keyword in text_lower:
                logger.debug(f'Remote work keyword found: {remote_keyword}')
                return True
        
        return False
    
    def matches_date_filter(self, message_date: datetime) -> bool:
        """Check if message is within the configured time window"""
        if self.date_filter_hours <= 0:
            return True  # No date filter
            
        # Ensure both dates are timezone-aware or timezone-naive
        if message_date.tzinfo is None:
            # Make message_date timezone-aware
            from datetime import timezone
            message_date = message_date.replace(tzinfo=timezone.utc)
            
        cutoff_time = datetime.now(message_date.tzinfo) - timedelta(hours=self.date_filter_hours)
        return message_date >= cutoff_time
    
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
    
    def get_experience_info(self, text: str) -> Dict[str, Any]:
        """Extract experience information from text"""
        if not text:
            return {}
            
        text_lower = text.lower()
        
        # Check for junior keywords
        junior_found = any(junior_keyword in text_lower for junior_keyword in self.junior_keywords)
        
        # Check for experience patterns
        experience_years = None
        for pattern in self.experience_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                try:
                    experience_years = int(matches[0])
                    break
                except ValueError:
                    continue
        
        # Check for remote work
        remote_found = any(remote_keyword in text_lower for remote_keyword in self.remote_keywords)
        
        return {
            'is_junior': junior_found,
            'experience_years': experience_years,
            'is_remote': remote_found,
            'meets_requirements': (junior_found or (experience_years is not None and experience_years <= 2)) and remote_found
        }

class MessageFilter:
    """Legacy filter class for backward compatibility"""
    
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
            
        # Ensure both dates are timezone-aware or timezone-naive
        if message_date.tzinfo is None:
            # Make message_date timezone-aware
            from datetime import timezone
            message_date = message_date.replace(tzinfo=timezone.utc)
            
        cutoff_time = datetime.now(message_date.tzinfo) - timedelta(hours=self.date_filter_hours)
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