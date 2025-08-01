import re
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """Clean and normalize text for better matching"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters that might interfere with matching
    text = re.sub(r'[^\w\s\-.,!?£$€@#%&*()]', '', text)
    
    return text.lower()

def extract_salary_info(text: str) -> Optional[Dict[str, Any]]:
    """Extract salary information from text"""
    salary_patterns = [
        # £50k, £50,000
        (r'£(\d{1,3}(?:,\d{3})*(?:\s*k)?)', 'GBP'),
        # $50k, $50,000
        (r'\$(\d{1,3}(?:,\d{3})*(?:\s*k)?)', 'USD'),
        # €50k, €50,000
        (r'€(\d{1,3}(?:,\d{3})*(?:\s*k)?)', 'EUR'),
        # 50k pounds, 50,000 GBP
        (r'(\d{1,3}(?:,\d{3})*(?:\s*k)?)\s*(?:pounds?|gbp)', 'GBP'),
        # 50k dollars, 50,000 USD
        (r'(\d{1,3}(?:,\d{3})*(?:\s*k)?)\s*(?:dollars?|usd)', 'USD'),
    ]
    
    for pattern, currency in salary_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            try:
                # Convert to number
                salary_str = matches[0].replace(',', '').replace('k', '000')
                salary = int(salary_str)
                return {
                    'amount': salary,
                    'currency': currency,
                    'formatted': f"{currency} {salary:,}"
                }
            except ValueError:
                continue
    
    return None

def extract_contact_info(text: str) -> Dict[str, Any]:
    """Extract contact information from text"""
    contact_info = {
        'email': None,
        'phone': None,
        'website': None,
        'linkedin': None
    }
    
    # Email patterns
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, text)
    if email_match:
        contact_info['email'] = email_match.group()
    
    # Phone patterns
    phone_patterns = [
        r'\+?[\d\s\-\(\)]{10,}',  # General phone pattern
        r'\+44\s*\d{4}\s*\d{6}',  # UK format
        r'\+1\s*\d{3}\s*\d{3}\s*\d{4}',  # US format
    ]
    
    for pattern in phone_patterns:
        phone_match = re.search(pattern, text)
        if phone_match:
            contact_info['phone'] = phone_match.group().strip()
            break
    
    # Website patterns
    website_pattern = r'https?://[^\s]+'
    website_match = re.search(website_pattern, text)
    if website_match:
        contact_info['website'] = website_match.group()
    
    # LinkedIn patterns
    linkedin_pattern = r'linkedin\.com/in/[^\s]+'
    linkedin_match = re.search(linkedin_pattern, text)
    if linkedin_match:
        contact_info['linkedin'] = linkedin_match.group()
    
    return contact_info

def extract_tech_stack(text: str) -> List[str]:
    """Extract technology stack from text"""
    tech_keywords = [
        # Programming Languages
        'python', 'javascript', 'typescript', 'java', 'c#', 'c++', 'go', 'rust', 'php', 'ruby', 'swift', 'kotlin',
        # Frameworks
        'react', 'vue', 'angular', 'node.js', 'express', 'django', 'flask', 'spring', 'laravel', 'rails',
        # Databases
        'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'sqlite', 'oracle', 'sql server',
        # Cloud & DevOps
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'gitlab', 'github actions', 'terraform',
        # Frontend
        'html', 'css', 'sass', 'less', 'bootstrap', 'tailwind', 'webpack', 'vite', 'next.js', 'nuxt.js',
        # Mobile
        'react native', 'flutter', 'ionic', 'xamarin', 'swift ui', 'kotlin android',
        # Other
        'graphql', 'rest api', 'microservices', 'serverless', 'machine learning', 'ai', 'blockchain'
    ]
    
    found_tech = []
    text_lower = text.lower()
    
    for tech in tech_keywords:
        if tech in text_lower:
            found_tech.append(tech)
    
    return found_tech

def extract_location_info(text: str) -> Optional[str]:
    """Extract location information from text"""
    # Common UK cities
    uk_cities = [
        'london', 'manchester', 'birmingham', 'leeds', 'liverpool', 'sheffield', 'bristol', 'glasgow',
        'edinburgh', 'cardiff', 'newcastle', 'belfast', 'nottingham', 'leicester', 'cambridge', 'oxford'
    ]
    
    # Common remote keywords
    remote_keywords = ['remote', 'work from home', 'wfh', 'hybrid', 'flexible working']
    
    text_lower = text.lower()
    
    # Check for remote work
    for keyword in remote_keywords:
        if keyword in text_lower:
            return 'Remote'
    
    # Check for UK cities
    for city in uk_cities:
        if city in text_lower:
            return city.title()
    
    return None

def format_message_for_display(message: Dict[str, Any]) -> str:
    """Format a message for display purposes"""
    text = message.get('message', '')[:200]
    if len(message.get('message', '')) > 200:
        text += "..."
    
    date_str = message.get('date', 'Unknown')
    if hasattr(date_str, 'strftime'):
        date_str = date_str.strftime('%Y-%m-%d %H:%M')
    
    return f"[{date_str}] {message.get('chat_title', 'Unknown')}: {text}"

def calculate_message_stats(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate statistics for a list of messages"""
    if not messages:
        return {
            'total_messages': 0,
            'unique_channels': 0,
            'date_range': None,
            'avg_message_length': 0
        }
    
    # Basic stats
    total_messages = len(messages)
    unique_channels = len(set(msg.get('chat_title', 'Unknown') for msg in messages))
    
    # Date range
    dates = [msg.get('date') for msg in messages if msg.get('date')]
    if dates:
        min_date = min(dates)
        max_date = max(dates)
        date_range = f"{min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}"
    else:
        date_range = None
    
    # Average message length
    message_lengths = [len(msg.get('message', '')) for msg in messages]
    avg_message_length = sum(message_lengths) / len(message_lengths) if message_lengths else 0
    
    return {
        'total_messages': total_messages,
        'unique_channels': unique_channels,
        'date_range': date_range,
        'avg_message_length': round(avg_message_length, 2)
    }

def validate_channel_id(channel_id: str) -> bool:
    """Validate if a channel ID is in the correct format"""
    try:
        # Channel IDs should be integers
        int(channel_id)
        return True
    except ValueError:
        return False

def get_channel_id_from_username(username: str) -> Optional[str]:
    """Extract channel ID from username or URL"""
    # Remove @ if present
    username = username.lstrip('@')
    
    # Remove t.me/ prefix if present
    if username.startswith('t.me/'):
        username = username[5:]
    
    # Remove https://t.me/ prefix if present
    if username.startswith('https://t.me/'):
        username = username[13:]
    
    return username

def create_backup_filename(prefix: str = 'backup') -> str:
    """Create a backup filename with timestamp"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{prefix}_{timestamp}.json"

def safe_json_dump(data: Any, filepath: str) -> bool:
    """Safely dump data to JSON file"""
    try:
        import json
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        logger.info(f'Data safely saved to {filepath}')
        return True
    except Exception as e:
        logger.error(f'Failed to save data to {filepath}: {e}')
        return False

def safe_json_load(filepath: str) -> Optional[Any]:
    """Safely load data from JSON file"""
    try:
        import json
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f'Data loaded from {filepath}')
        return data
    except Exception as e:
        logger.error(f'Failed to load data from {filepath}: {e}')
        return None