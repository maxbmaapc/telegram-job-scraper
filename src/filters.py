import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
from decimal import Decimal

# Try to import salary_extractor, but provide fallback if it fails
try:
    from .salary_extractor import salary_extractor, extract_salary_from_text
except ImportError:
    # Fallback for when running outside of package context
    class MockSalaryExtractor:
        def extract_salaries(self, text):
            return []
        
        def normalize_to_yearly(self, salary):
            return None
    
    salary_extractor = MockSalaryExtractor()
    extract_salary_from_text = lambda x: []

# Try to import logging_config, but provide fallback if it fails
try:
    from .logging_config import get_logger
except ImportError:
    # Fallback for when running outside of package context
    def get_logger(name):
        return logging.getLogger(name)

logger = get_logger(__name__)

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
        
        # Enhanced keywords to exclude (resumes/CVs - more comprehensive)
        self.resume_exclude_keywords = [
            # Direct resume/CV indicators
            'резюме', 'cv', 'resume', 'curriculum vitae', 'curriculum vitae',
            'анкета', 'application', 'заявка', 'портфолио', 'portfolio',
            
            # Job seeking indicators
            'ищу работу', 'looking for job', 'seeking position', 'seeking job',
            'открыт к предложениям', 'open to opportunities', 'open to offers',
            'готов к переезду', 'willing to relocate', 'готов к релокации',
            'активно ищу', 'actively seeking', 'job search', 'поиск работы',
            'job hunting', 'career change', 'смена карьеры', 'смена работы',
            'переход в компанию', 'company transition', 'смена работодателя',
            'новые возможности', 'new opportunities', 'новые проекты',
            'job switch', 'career move', 'смена направления',
            
            # Availability indicators
            'доступен для проектов', 'available for projects', 'свободен',
            'ищу проект', 'looking for project', 'ищу заказчика',
            'готов к сотрудничеству', 'ready to collaborate',
            'ищу команду', 'looking for team', 'ищу компанию',
            
            # Experience description (often in resumes)
            'имею опыт в', 'have experience in', 'работал с', 'worked with',
            'мои навыки', 'my skills', 'мои технологии', 'my technologies',
            'знаю', 'know', 'изучал', 'studied', 'изучаю', 'studying',
            
            # Personal pronouns (common in resumes)
            'я разработчик', 'i am developer', 'я программист', 'i am programmer',
            'моя специализация', 'my specialization', 'мои интересы', 'my interests'
        ]
        
        # Strict junior keywords - only accept developer/engineer positions
        self.junior_keywords = [
            'junior developer', 'джуниор разработчик', 'junior разработчик',
            'junior engineer', 'джуниор инженер', 'junior инженер',
            'junior software developer', 'джуниор программист', 'junior программист',
            'junior software engineer', 'джуниор софт инженер',
            'стажер разработчик', 'intern developer', 'стажировка разработчик',
            'trainee developer', 'трени разработчик', 'trainee engineer',
            'entry level developer', 'entry-level developer', 'начальный уровень разработчик',
            'без опыта разработчик', 'no experience developer', 'опыт не требуется разработчик',
            # Additional variations
            'junior python developer', 'junior javascript developer', 'junior js developer',
            'junior react developer', 'junior web3 developer', 'junior blockchain developer',
            'junior frontend developer', 'junior backend developer', 'junior full stack developer',
            'джуниор python разработчик', 'джуниор javascript разработчик', 'джуниор js разработчик',
            'джуниор react разработчик', 'джуниор web3 разработчик', 'джуниор blockchain разработчик'
        ]
        
        # Keywords that indicate it's NOT a developer/engineer position (reject these)
        # Note: web3 and blockchain are allowed when combined with developer/engineer keywords
        self.non_developer_keywords = [
            'маркетинг', 'marketing', 'продажи', 'sales', 'менеджер', 'manager',
            'аналитик', 'analyst', 'дизайнер', 'designer', 'тестировщик', 'tester',
            'qa', 'quality assurance', 'devops', 'системный администратор', 'sysadmin',
            'data scientist', 'data analyst', 'product manager', 'project manager',
            'hr', 'human resources', 'рекрутер', 'recruiter', 'бухгалтер', 'accountant'
        ]
        
        # Keywords that are only allowed when combined with developer/engineer terms
        self.contextual_keywords = [
            'web3', 'web 3', 'blockchain', 'crypto', 'nft', 'defi'
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
                logger.debug('Message excluded: no text content')
                return False
            
            # Check keyword filter
            if not self.matches_keywords(text):
                logger.debug('Message excluded: no keyword matches')
                return False
            
            # Check date filter
            message_date = self._extract_message_date(message)
            if not self.matches_date_filter(message_date):
                logger.debug('Message excluded: outside date filter window')
                return False
            
            # Check exclude keywords (senior/middle positions)
            if self.has_exclude_keywords(text):
                logger.debug(f'Message excluded: contains senior/middle keywords')
                return False
            
            # Check resume/CV keywords (enhanced detection)
            if self.has_resume_keywords(text):
                logger.debug(f'Message excluded: contains resume/CV keywords')
                return False
            
            # Check if it's a non-developer position
            if self.has_non_developer_keywords(text):
                logger.debug(f'Message excluded: contains non-developer keywords')
                return False
            
            # Check experience requirements
            if not self.matches_experience_requirements(text):
                logger.debug(f'Message excluded: does not meet experience requirements')
                return False
            
            # Check remote work requirement
            if not self.matches_remote_requirement(text):
                logger.debug(f'Message excluded: no remote work mentioned')
                return False
            
            logger.debug('Message passed all filters successfully')
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
    
    def has_resume_keywords(self, text: str) -> bool:
        """Check if text contains resume/CV keywords (enhanced detection)"""
        if not text:
            return False
            
        text_lower = text.lower()
        
        # Check for resume keywords with context
        for resume_keyword in self.resume_exclude_keywords:
            if resume_keyword in text_lower:
                logger.debug(f'Found resume keyword: "{resume_keyword}"')
                # Additional context check to reduce false positives
                if self._is_likely_resume_context(text_lower, resume_keyword):
                    logger.debug(f'Resume keyword "{resume_keyword}" confirmed in resume context')
                    return True
                else:
                    logger.debug(f'Resume keyword "{resume_keyword}" found but not in resume context - allowing through')
        
        return False
    
    def _is_likely_resume_context(self, text: str, keyword: str) -> bool:
        """Check if the keyword appears in a resume-like context"""
        # If it's a direct resume indicator, it's likely a resume
        direct_indicators = ['резюме', 'cv', 'resume', 'curriculum vitae', 'анкета', 'application']
        if keyword in direct_indicators:
            logger.debug(f'Direct resume indicator found: "{keyword}"')
            return True
        
        # Check for personal pronouns near the keyword (common in resumes)
        personal_indicators = ['я', 'i', 'моя', 'my', 'меня', 'me', 'мне', 'to me']
        for indicator in personal_indicators:
            if indicator in text:
                # Check if personal indicator is close to the keyword
                keyword_pos = text.find(keyword)
                indicator_pos = text.find(indicator)
                if abs(keyword_pos - indicator_pos) < 100:  # Within 100 characters
                    logger.debug(f'Personal indicator "{indicator}" found near resume keyword "{keyword}"')
                    return True
        
        # Check for job-seeking language patterns
        seeking_patterns = [
            r'ищу\s+работу', r'looking\s+for\s+job', r'seeking\s+position',
            r'открыт\s+к\s+предложениям', r'open\s+to\s+opportunities'
        ]
        for pattern in seeking_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                logger.debug(f'Job-seeking pattern found: "{pattern}"')
                return True
        
        return False
    
    def has_non_developer_keywords(self, text: str) -> bool:
        """Check if text contains keywords indicating non-developer positions"""
        if not text:
            return False
            
        text_lower = text.lower()
        
        # Check for non-developer keywords
        for non_dev_keyword in self.non_developer_keywords:
            if non_dev_keyword in text_lower:
                logger.debug(f'Found non-developer keyword: "{non_dev_keyword}"')
                return True
        
        # Check for contextual keywords (web3, blockchain, etc.) - only reject if NOT combined with developer terms
        for contextual_keyword in self.contextual_keywords:
            if contextual_keyword in text_lower:
                # Check if it's combined with developer/engineer terms
                developer_terms = ['developer', 'engineer', 'разработчик', 'инженер', 'программист']
                has_developer_term = any(term in text_lower for term in developer_terms)
                
                if not has_developer_term:
                    logger.debug(f'Found contextual keyword "{contextual_keyword}" without developer terms - rejecting')
                    return True
                else:
                    logger.debug(f'Found contextual keyword "{contextual_keyword}" with developer terms - allowing')
        
        return False
    
    def matches_experience_requirements(self, text: str) -> bool:
        """Check if message matches experience requirements"""
        if not text:
            return False
            
        text_lower = text.lower()
        
        # Check for strict junior keywords (only developer/engineer positions)
        for junior_keyword in self.junior_keywords:
            if junior_keyword in text_lower:
                logger.debug(f'Found junior keyword: "{junior_keyword}"')
                # Additional check: make sure it's not combined with non-developer keywords
                if not self.has_non_developer_keywords(text_lower):
                    logger.debug(f'Junior keyword "{junior_keyword}" confirmed for developer position')
                    return True
                else:
                    logger.debug(f'Junior keyword "{junior_keyword}" found but combined with non-developer keywords - rejecting')
                    return False
        
        # Check experience patterns
        for pattern in self.experience_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                try:
                    years = int(match)
                    logger.debug(f'Found experience requirement: {years} years')
                    # Accept if experience is 2 years or less
                    if years <= 2:
                        logger.debug(f'Experience requirement {years} years is acceptable')
                        return True
                    else:
                        logger.debug(f'Experience requirement {years} years is too high')
                        return False
                except ValueError:
                    continue
        
        # If no experience mentioned and no junior keywords, accept (could be entry level)
        logger.debug('No specific experience requirements found, accepting as potential entry level')
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
        
        # Handle None dates
        if message_date is None:
            logger.debug('Message has no date, accepting by default')
            return True
            
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
        
        # Check for strict junior keywords
        junior_found = any(junior_keyword in text_lower for junior_keyword in self.junior_keywords)
        
        # Check for non-developer keywords
        non_dev_found = self.has_non_developer_keywords(text_lower)
        
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
            'is_junior': junior_found and not non_dev_found,
            'experience_years': experience_years,
            'is_remote': remote_found,
            'is_developer_position': not non_dev_found,
            'meets_requirements': (junior_found and not non_dev_found) or (experience_years is not None and experience_years <= 2 and not non_dev_found) and remote_found
        }
    
    def get_salary_info(self, text: str) -> Dict[str, Any]:
        """Extract salary information from text using enhanced salary extraction"""
        if not text:
            return {}
        
        try:
            salaries = salary_extractor.extract_salaries(text)
            
            if not salaries:
                return {'salaries_found': False}
            
            # Convert to dictionaries
            salary_data = [salary.to_dict() for salary in salaries]
            
            # Get the primary salary (first one found)
            primary_salary = salary_data[0] if salary_data else None
            
            return {
                'salaries_found': True,
                'salary_count': len(salary_data),
                'primary_salary': primary_salary,
                'all_salaries': salary_data
            }
            
        except Exception as e:
            logger.error(f"Error extracting salary info: {e}")
            return {'salaries_found': False, 'error': str(e)}
    
    def get_job_analysis(self, text: str) -> Dict[str, Any]:
        """Comprehensive job analysis including experience and salary information"""
        if not text:
            return {}
        
        experience_info = self.get_experience_info(text)
        salary_info = self.get_salary_info(text)
        
        return {
            'experience': experience_info,
            'salary': salary_info,
            'matched_keywords': self.get_matched_keywords(text),
            'excluded_keywords': self._get_excluded_keywords(text),
            'remote_work_mentioned': experience_info.get('is_remote', False),
            'junior_position': experience_info.get('is_junior', False),
            'developer_position': experience_info.get('is_developer_position', False)
        }
    
    def _get_excluded_keywords(self, text: str) -> List[str]:
        """Get list of exclude keywords found in text"""
        if not text:
            return []
            
        text_lower = text.lower()
        found = []
        
        for exclude_keyword in self.exclude_keywords:
            if exclude_keyword in text_lower:
                found.append(exclude_keyword)
        
        # Also check for resume keywords
        for resume_keyword in self.resume_exclude_keywords:
            if resume_keyword in text_lower:
                found.append(f"resume: {resume_keyword}")
        
        # Check for non-developer keywords
        for non_dev_keyword in self.non_developer_keywords:
            if non_dev_keyword in text_lower:
                found.append(f"non-dev: {non_dev_keyword}")
        
        # Check for contextual keywords
        for contextual_keyword in self.contextual_keywords:
            if contextual_keyword in text_lower:
                # Check if it's combined with developer terms
                developer_terms = ['developer', 'engineer', 'разработчик', 'инженер', 'программист']
                has_developer_term = any(term in text_lower for term in developer_terms)
                
                if has_developer_term:
                    found.append(f"contextual: {contextual_keyword} (with developer terms)")
                else:
                    found.append(f"contextual: {contextual_keyword} (without developer terms)")
        
        return found

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
        """Check if message contains salary within specified range using enhanced salary extraction"""
        if not (self.min_salary or self.max_salary):
            return True  # No salary filter, pass all
        
        try:
            # Extract salaries using the enhanced salary extractor
            salaries = salary_extractor.extract_salaries(text)
            
            if not salaries:
                logger.debug("No salary found in text")
                return False
            
            # Check each extracted salary
            for salary in salaries:
                # Normalize to yearly for comparison
                yearly_salary = salary_extractor.normalize_to_yearly(salary)
                
                # Convert to target currency if needed (simplified)
                if yearly_salary.currency != 'USD':
                    # For now, assume USD as target currency
                    # In production, implement proper currency conversion
                    pass
                
                # Check if salary meets criteria
                if self.min_salary:
                    if yearly_salary.max_amount and yearly_salary.max_amount < Decimal(str(self.min_salary)):
                        continue
                
                if self.max_salary:
                    if yearly_salary.min_amount and yearly_salary.min_amount > Decimal(str(self.max_salary)):
                        continue
                
                logger.debug(f"Salary {yearly_salary} matches criteria")
                return True
            
            logger.debug("No salary matches the specified range")
            return False
            
        except Exception as e:
            logger.error(f"Error checking salary range: {e}")
            return False  # Fail safe - don't exclude on error