"""
Advanced salary extraction and parsing module.

This module provides comprehensive salary extraction capabilities for job postings,
supporting multiple currencies, formats, and edge cases.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import locale

logger = logging.getLogger(__name__)

@dataclass
class SalaryRange:
    """Represents a salary range with currency and period information."""
    min_amount: Optional[Decimal]
    max_amount: Optional[Decimal]
    currency: str
    period: str  # 'hourly', 'daily', 'weekly', 'monthly', 'yearly'
    is_range: bool
    raw_text: str
    
    def __post_init__(self):
        """Validate and normalize the salary range."""
        if self.min_amount is not None and self.max_amount is not None:
            if self.min_amount > self.max_amount:
                # Swap if min > max
                self.min_amount, self.max_amount = self.max_amount, self.min_amount
        
        # Normalize currency to uppercase
        self.currency = self.currency.upper()
        
        # Normalize period
        period_mapping = {
            'hour': 'hourly', 'hr': 'hourly', 'hourly': 'hourly',
            'day': 'daily', 'daily': 'daily',
            'week': 'weekly', 'weekly': 'weekly',
            'month': 'monthly', 'mo': 'monthly', 'monthly': 'monthly',
            'year': 'yearly', 'yr': 'yearly', 'annum': 'yearly', 'annual': 'yearly', 'yearly': 'yearly'
        }
        self.period = period_mapping.get(self.period.lower(), 'yearly')
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            'min_amount': float(self.min_amount) if self.min_amount else None,
            'max_amount': float(self.max_amount) if self.max_amount else None,
            'currency': self.currency,
            'period': self.period,
            'is_range': self.is_range,
            'raw_text': self.raw_text
        }
    
    def __str__(self) -> str:
        """String representation of the salary range."""
        if self.is_range:
            return f"{self.min_amount}-{self.max_amount} {self.currency} ({self.period})"
        else:
            return f"{self.min_amount} {self.currency} ({self.period})"

class SalaryExtractor:
    """Advanced salary extraction from job posting text."""
    
    def __init__(self):
        # Currency symbols and codes
        self.currencies = {
            '$': 'USD', '€': 'EUR', '£': 'GBP', '¥': 'JPY', '₹': 'INR',
            '₽': 'RUB', '₴': 'UAH', '₸': 'KZT', '₿': 'BTC',
            'usd': 'USD', 'eur': 'EUR', 'gbp': 'GBP', 'jpy': 'JPY',
            'dollars': 'USD', 'euros': 'EUR', 'pounds': 'GBP',
            'руб': 'RUB', 'рублей': 'RUB', 'рубля': 'RUB',
            'гривен': 'UAH', 'гривна': 'UAH', 'гривны': 'UAH',
            'тенге': 'KZT'
        }
        
        # Period keywords
        self.period_keywords = {
            'hourly': ['hour', 'hr', 'hourly', 'per hour', '/hr', '/hour'],
            'daily': ['day', 'daily', 'per day', '/day'],
            'weekly': ['week', 'weekly', 'per week', '/week'],
            'monthly': ['month', 'mo', 'monthly', 'per month', '/month'],
            'yearly': ['year', 'yr', 'annum', 'annual', 'yearly', 'per annum', 'per year', '/year', 'pa']
        }
        
        # Common salary patterns
        self.salary_patterns = [
            # Basic patterns: $50k, £50,000, €50k
            r'([$€£¥₹₽₴₸₿])\s*(\d{1,3}(?:,\d{3})*(?:\s*k)?)',
            r'(\d{1,3}(?:,\d{3})*(?:\s*k)?)\s*([$€£¥₹₽₴₸₿])',
            
            # Text currency: 50k USD, 50,000 dollars
            r'(\d{1,3}(?:,\d{3})*(?:\s*k)?)\s*(usd|eur|gbp|jpy|inr|rub|uah|kzt|btc|dollars?|euros?|pounds?|руб(?:лей|я)?|гривен?|тенге)',
            
            # Range patterns: $50k-$80k, £50,000-80,000
            r'([$€£¥₹₽₴₸₿])\s*(\d{1,3}(?:,\d{3})*(?:\s*k)?)\s*[-–—]\s*(\d{1,3}(?:,\d{3})*(?:\s*k)?)',
            r'(\d{1,3}(?:,\d{3})*(?:\s*k)?)\s*[-–—]\s*(\d{1,3}(?:,\d{3})*(?:\s*k)?)\s*([$€£¥₹₽₴₸₿])',
            
            # Text range: 50k-80k USD
            r'(\d{1,3}(?:,\d{3})*(?:\s*k)?)\s*[-–—]\s*(\d{1,3}(?:,\d{3})*(?:\s*k)?)\s*(usd|eur|gbp|jpy|inr|rub|uah|kzt|btc|dollars?|euros?|pounds?|руб(?:лей|я)?|гривен?|тенге)',
            
            # With period: $50k/year, £50,000 per annum
            r'([$€£¥₹₽₴₸₿])\s*(\d{1,3}(?:,\d{3})*(?:\s*k)?)\s*(?:per\s+)?(hour|day|week|month|year|annum|annual)',
            r'(\d{1,3}(?:,\d{3})*(?:\s*k)?)\s*(?:per\s+)?(hour|day|week|month|year|annum|annual)\s*([$€£¥₹₽₴₸₿])',
            
            # Complex patterns: salary between $50k and $80k
            r'(?:salary|pay|compensation)\s+(?:between|from|range)\s+([$€£¥₹₽₴₸₿])\s*(\d{1,3}(?:,\d{3})*(?:\s*k)?)\s*(?:and|to)\s+([$€£¥₹₽₴₸₿])\s*(\d{1,3}(?:,\d{3})*(?:\s*k)?)',
            
            # Russian patterns: от 100000 до 200000 рублей
            r'от\s+(\d{1,3}(?:,\d{3})*(?:\s*k)?)\s+до\s+(\d{1,3}(?:,\d{3})*(?:\s*k)?)\s*(руб(?:лей|я)?|гривен?|тенге)',
            r'(\d{1,3}(?:,\d{3})*(?:\s*k)?)\s*[-–—]\s*(\d{1,3}(?:,\d{3})*(?:\s*k)?)\s*(руб(?:лей|я)?|гривен?|тенге)',
        ]
        
        # Compile patterns for better performance
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.salary_patterns]
    
    def extract_salaries(self, text: str) -> List[SalaryRange]:
        """
        Extract all salary information from text.
        
        Args:
            text: Job posting text to analyze
            
        Returns:
            List of extracted salary ranges
        """
        if not text:
            return []
        
        salaries = []
        text_lower = text.lower()
        
        # Try each pattern
        for pattern in self.compiled_patterns:
            matches = pattern.finditer(text)
            for match in matches:
                try:
                    salary = self._parse_match(match, text)
                    if salary:
                        salaries.append(salary)
                except Exception as e:
                    logger.debug(f"Failed to parse salary match: {match.group()} - {e}")
        
        # Remove duplicates and sort by amount
        unique_salaries = self._deduplicate_salaries(salaries)
        return sorted(unique_salaries, key=lambda s: s.min_amount or Decimal('0'))
    
    def _parse_match(self, match: re.Match, original_text: str) -> Optional[SalaryRange]:
        """Parse a regex match into a SalaryRange object."""
        groups = match.groups()
        raw_text = match.group(0)
        
        # Determine pattern type and extract values
        if len(groups) == 2:
            # Single amount: $50k or 50k USD
            if groups[0] in self.currencies:
                currency = self.currencies[groups[0]]
                amount = self._parse_amount(groups[1])
                period = self._detect_period(original_text, match.start())
                return SalaryRange(
                    min_amount=amount,
                    max_amount=None,
                    currency=currency,
                    period=period,
                    is_range=False,
                    raw_text=raw_text
                )
            else:
                amount = self._parse_amount(groups[0])
                currency = self.currencies.get(groups[1].lower(), 'USD')
                period = self._detect_period(original_text, match.start())
                return SalaryRange(
                    min_amount=amount,
                    max_amount=None,
                    currency=currency,
                    period=period,
                    is_range=False,
                    raw_text=raw_text
                )
        
        elif len(groups) == 3:
            # Range: $50k-$80k or 50k-80k USD
            if groups[0] in self.currencies:
                currency = self.currencies[groups[0]]
                min_amount = self._parse_amount(groups[1])
                max_amount = self._parse_amount(groups[2])
                period = self._detect_period(original_text, match.start())
                return SalaryRange(
                    min_amount=min_amount,
                    max_amount=max_amount,
                    currency=currency,
                    period=period,
                    is_range=True,
                    raw_text=raw_text
                )
            else:
                min_amount = self._parse_amount(groups[0])
                max_amount = self._parse_amount(groups[1])
                currency = self.currencies.get(groups[2].lower(), 'USD')
                period = self._detect_period(original_text, match.start())
                return SalaryRange(
                    min_amount=min_amount,
                    max_amount=max_amount,
                    currency=currency,
                    period=period,
                    is_range=True,
                    raw_text=raw_text
                )
        
        elif len(groups) == 4:
            # Complex range: $50k and $80k
            currency = self.currencies[groups[0]]
            min_amount = self._parse_amount(groups[1])
            max_amount = self._parse_amount(groups[3])
            period = self._detect_period(original_text, match.start())
            return SalaryRange(
                min_amount=min_amount,
                max_amount=max_amount,
                currency=currency,
                period=period,
                is_range=True,
                raw_text=raw_text
            )
        
        return None
    
    def _parse_amount(self, amount_str: str) -> Optional[Decimal]:
        """Parse amount string to Decimal."""
        if not amount_str:
            return None
        
        # Remove commas and convert k to thousands
        amount_str = amount_str.replace(',', '').strip()
        
        # Handle 'k' suffix (thousands)
        if amount_str.lower().endswith('k'):
            amount_str = amount_str[:-1] + '000'
        
        try:
            return Decimal(amount_str)
        except (InvalidOperation, ValueError):
            logger.debug(f"Failed to parse amount: {amount_str}")
            return None
    
    def _detect_period(self, text: str, position: int) -> str:
        """Detect salary period from surrounding text."""
        # Look for period keywords around the match position
        context_start = max(0, position - 100)
        context_end = min(len(text), position + 100)
        context = text[context_start:context_end].lower()
        
        for period, keywords in self.period_keywords.items():
            for keyword in keywords:
                if keyword in context:
                    return period
        
        # Default to yearly
        return 'yearly'
    
    def _deduplicate_salaries(self, salaries: List[SalaryRange]) -> List[SalaryRange]:
        """Remove duplicate salary ranges."""
        unique_salaries = []
        seen = set()
        
        for salary in salaries:
            # Create a key for deduplication
            key = (
                salary.min_amount,
                salary.max_amount,
                salary.currency,
                salary.period
            )
            
            if key not in seen:
                seen.add(key)
                unique_salaries.append(salary)
        
        return unique_salaries
    
    def normalize_to_yearly(self, salary: SalaryRange) -> SalaryRange:
        """Convert salary to yearly equivalent."""
        if salary.period == 'yearly':
            return salary
        
        # Conversion factors
        conversions = {
            'hourly': 2080,  # 40 hours/week * 52 weeks
            'daily': 260,    # 5 days/week * 52 weeks
            'weekly': 52,    # 52 weeks/year
            'monthly': 12    # 12 months/year
        }
        
        factor = conversions.get(salary.period, 1)
        
        if salary.min_amount:
            salary.min_amount *= factor
        if salary.max_amount:
            salary.max_amount *= factor
        
        salary.period = 'yearly'
        return salary
    
    def filter_by_range(self, salaries: List[SalaryRange], 
                       min_salary: Optional[Decimal] = None,
                       max_salary: Optional[Decimal] = None,
                       currency: str = 'USD') -> List[SalaryRange]:
        """Filter salaries by range and currency."""
        filtered = []
        
        for salary in salaries:
            # Normalize to yearly for comparison
            yearly_salary = self.normalize_to_yearly(salary)
            
            # Convert currency if needed (simplified - in production, use real exchange rates)
            if yearly_salary.currency != currency:
                yearly_salary = self._convert_currency(yearly_salary, currency)
            
            # Check range
            if min_salary and yearly_salary.max_amount and yearly_salary.max_amount < min_salary:
                continue
            if max_salary and yearly_salary.min_amount and yearly_salary.min_amount > max_salary:
                continue
            
            filtered.append(salary)
        
        return filtered
    
    def _convert_currency(self, salary: SalaryRange, target_currency: str) -> SalaryRange:
        """Convert salary to target currency (simplified implementation)."""
        # This is a simplified conversion - in production, use real exchange rates
        # For now, just return the original salary
        return salary

# Global extractor instance
salary_extractor = SalaryExtractor()

def extract_salary_from_text(text: str) -> List[Dict]:
    """
    Convenience function to extract salaries from text.
    
    Args:
        text: Job posting text
        
    Returns:
        List of salary dictionaries
    """
    salaries = salary_extractor.extract_salaries(text)
    return [salary.to_dict() for salary in salaries]

def extract_salary_range(text: str) -> Optional[Dict]:
    """
    Extract the most likely salary range from text.
    
    Args:
        text: Job posting text
        
    Returns:
        Most likely salary range or None
    """
    salaries = salary_extractor.extract_salaries(text)
    if not salaries:
        return None
    
    # Return the first (most likely) salary
    return salaries[0].to_dict() 