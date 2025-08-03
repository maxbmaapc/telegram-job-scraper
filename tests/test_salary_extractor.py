"""
Tests for the salary extraction module.

This module tests the enhanced salary extraction capabilities including
various currency formats, patterns, and edge cases.
"""

import pytest
import sys
import os
from decimal import Decimal

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from salary_extractor import SalaryExtractor, SalaryRange, extract_salary_from_text, extract_salary_range

class TestSalaryRange:
    """Test cases for SalaryRange dataclass."""
    
    def test_salary_range_creation(self):
        """Test creating a salary range."""
        salary = SalaryRange(
            min_amount=Decimal('50000'),
            max_amount=Decimal('80000'),
            currency='USD',
            period='yearly',
            is_range=True,
            raw_text='$50k-$80k'
        )
        
        assert salary.min_amount == Decimal('50000')
        assert salary.max_amount == Decimal('80000')
        assert salary.currency == 'USD'
        assert salary.period == 'yearly'
        assert salary.is_range is True
    
    def test_salary_range_normalization(self):
        """Test salary range normalization (swapping min/max if needed)."""
        salary = SalaryRange(
            min_amount=Decimal('80000'),
            max_amount=Decimal('50000'),
            currency='USD',
            period='yearly',
            is_range=True,
            raw_text='$80k-$50k'
        )
        
        # Should be normalized
        assert salary.min_amount == Decimal('50000')
        assert salary.max_amount == Decimal('80000')
    
    def test_currency_normalization(self):
        """Test currency normalization to uppercase."""
        salary = SalaryRange(
            min_amount=Decimal('50000'),
            max_amount=None,
            currency='usd',
            period='yearly',
            is_range=False,
            raw_text='$50k'
        )
        
        assert salary.currency == 'USD'
    
    def test_period_normalization(self):
        """Test period normalization."""
        test_cases = [
            ('hour', 'hourly'),
            ('hr', 'hourly'),
            ('day', 'daily'),
            ('week', 'weekly'),
            ('month', 'monthly'),
            ('mo', 'monthly'),
            ('year', 'yearly'),
            ('yr', 'yearly'),
            ('annum', 'yearly'),
            ('annual', 'yearly'),
            ('unknown', 'yearly')  # Default
        ]
        
        for input_period, expected_period in test_cases:
            salary = SalaryRange(
                min_amount=Decimal('50000'),
                max_amount=None,
                currency='USD',
                period=input_period,
                is_range=False,
                raw_text='$50k'
            )
            assert salary.period == expected_period
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        salary = SalaryRange(
            min_amount=Decimal('50000'),
            max_amount=Decimal('80000'),
            currency='USD',
            period='yearly',
            is_range=True,
            raw_text='$50k-$80k'
        )
        
        result = salary.to_dict()
        expected = {
            'min_amount': 50000.0,
            'max_amount': 80000.0,
            'currency': 'USD',
            'period': 'yearly',
            'is_range': True,
            'raw_text': '$50k-$80k'
        }
        
        assert result == expected
    
    def test_string_representation(self):
        """Test string representation."""
        # Range
        salary_range = SalaryRange(
            min_amount=Decimal('50000'),
            max_amount=Decimal('80000'),
            currency='USD',
            period='yearly',
            is_range=True,
            raw_text='$50k-$80k'
        )
        assert str(salary_range) == '50000-80000 USD (yearly)'
        
        # Single amount
        salary_single = SalaryRange(
            min_amount=Decimal('50000'),
            max_amount=None,
            currency='USD',
            period='yearly',
            is_range=False,
            raw_text='$50k'
        )
        assert str(salary_single) == '50000 USD (yearly)'

class TestSalaryExtractor:
    """Test cases for SalaryExtractor class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.extractor = SalaryExtractor()
    
    def test_basic_currency_patterns(self):
        """Test basic currency symbol patterns."""
        test_cases = [
            ('$50k', 'USD'),
            ('£50,000', 'GBP'),
            ('€50k', 'EUR'),
            ('¥50000', 'JPY'),
            ('₽50000', 'RUB'),
            ('₴50000', 'UAH'),
            ('₸50000', 'KZT'),
            ('₿50000', 'BTC'),
        ]
        
        for text, expected_currency in test_cases:
            salaries = self.extractor.extract_salaries(text)
            assert len(salaries) > 0
            assert salaries[0].currency == expected_currency
    
    def test_text_currency_patterns(self):
        """Test text-based currency patterns."""
        test_cases = [
            ('50k USD', 'USD'),
            ('50,000 dollars', 'USD'),
            ('50k EUR', 'EUR'),
            ('50,000 euros', 'EUR'),
            ('50k GBP', 'GBP'),
            ('50,000 pounds', 'GBP'),
            ('50000 рублей', 'RUB'),
            ('50000 гривен', 'UAH'),
            ('50000 тенге', 'KZT'),
        ]
        
        for text, expected_currency in test_cases:
            salaries = self.extractor.extract_salaries(text)
            assert len(salaries) > 0
            assert salaries[0].currency == expected_currency
    
    def test_salary_ranges(self):
        """Test salary range extraction."""
        test_cases = [
            ('$50k-$80k', 50000, 80000),
            ('£50,000-80,000', 50000, 80000),
            ('50k-80k USD', 50000, 80000),
            ('от 100000 до 200000 рублей', 100000, 200000),
        ]
        
        for text, expected_min, expected_max in test_cases:
            salaries = self.extractor.extract_salaries(text)
            assert len(salaries) > 0
            salary = salaries[0]
            assert salary.is_range is True
            assert salary.min_amount == Decimal(str(expected_min))
            assert salary.max_amount == Decimal(str(expected_max))
    
    def test_period_detection(self):
        """Test salary period detection."""
        test_cases = [
            ('$50/hour', 'hourly'),
            ('$50 per hour', 'hourly'),
            ('$50/hr', 'hourly'),
            ('$1000/day', 'daily'),
            ('$1000 per day', 'daily'),
            ('$5000/week', 'weekly'),
            ('$5000 per week', 'weekly'),
            ('$10000/month', 'monthly'),
            ('$10000 per month', 'monthly'),
            ('$50000/year', 'yearly'),
            ('$50000 per annum', 'yearly'),
            ('$50000 pa', 'yearly'),
        ]
        
        for text, expected_period in test_cases:
            salaries = self.extractor.extract_salaries(text)
            assert len(salaries) > 0
            assert salaries[0].period == expected_period
    
    def test_complex_patterns(self):
        """Test complex salary patterns."""
        test_cases = [
            'Salary between $50k and $80k',
            'Pay range from $50,000 to $80,000',
            'Compensation: $50k-$80k USD',
            'Зарплата от 100000 до 200000 рублей',
        ]
        
        for text in test_cases:
            salaries = self.extractor.extract_salaries(text)
            assert len(salaries) > 0
            assert salaries[0].is_range is True
    
    def test_amount_parsing(self):
        """Test amount parsing with various formats."""
        test_cases = [
            ('50k', 50000),
            ('50,000', 50000),
            ('50000', 50000),
            ('1.5k', 1500),
            ('100k', 100000),
        ]
        
        for amount_str, expected in test_cases:
            result = self.extractor._parse_amount(amount_str)
            assert result == Decimal(str(expected))
    
    def test_invalid_amounts(self):
        """Test handling of invalid amounts."""
        invalid_amounts = ['', 'abc', 'k', '50abc', 'abc50']
        
        for amount_str in invalid_amounts:
            result = self.extractor._parse_amount(amount_str)
            assert result is None
    
    def test_deduplication(self):
        """Test salary deduplication."""
        text = "Salary: $50k, also $50k, and $50k again"
        salaries = self.extractor.extract_salaries(text)
        
        # Should only have one unique salary
        assert len(salaries) == 1
        assert salaries[0].min_amount == Decimal('50000')
    
    def test_normalize_to_yearly(self):
        """Test salary normalization to yearly."""
        test_cases = [
            (SalaryRange(Decimal('25'), None, 'USD', 'hourly', False, ''), 52000),  # 25 * 2080
            (SalaryRange(Decimal('200'), None, 'USD', 'daily', False, ''), 52000),  # 200 * 260
            (SalaryRange(Decimal('1000'), None, 'USD', 'weekly', False, ''), 52000),  # 1000 * 52
            (SalaryRange(Decimal('4000'), None, 'USD', 'monthly', False, ''), 48000),  # 4000 * 12
            (SalaryRange(Decimal('50000'), None, 'USD', 'yearly', False, ''), 50000),  # No change
        ]
        
        for salary, expected_yearly in test_cases:
            normalized = self.extractor.normalize_to_yearly(salary)
            assert normalized.period == 'yearly'
            assert normalized.min_amount == Decimal(str(expected_yearly))
    
    def test_filter_by_range(self):
        """Test salary filtering by range."""
        salaries = [
            SalaryRange(Decimal('30000'), None, 'USD', 'yearly', False, ''),
            SalaryRange(Decimal('50000'), None, 'USD', 'yearly', False, ''),
            SalaryRange(Decimal('80000'), None, 'USD', 'yearly', False, ''),
        ]
        
        # Filter by min salary
        filtered = self.extractor.filter_by_range(salaries, min_salary=Decimal('40000'))
        assert len(filtered) == 2  # 50k and 80k
        
        # Filter by max salary
        filtered = self.extractor.filter_by_range(salaries, max_salary=Decimal('60000'))
        assert len(filtered) == 2  # 30k and 50k
        
        # Filter by range
        filtered = self.extractor.filter_by_range(salaries, 
                                                 min_salary=Decimal('40000'),
                                                 max_salary=Decimal('60000'))
        assert len(filtered) == 1  # Only 50k

class TestConvenienceFunctions:
    """Test cases for convenience functions."""
    
    def test_extract_salary_from_text(self):
        """Test extract_salary_from_text function."""
        text = "We're looking for a developer with salary $50k-$80k USD"
        result = extract_salary_from_text(text)
        
        assert len(result) > 0
        assert result[0]['is_range'] is True
        assert result[0]['min_amount'] == 50000.0
        assert result[0]['max_amount'] == 80000.0
        assert result[0]['currency'] == 'USD'
    
    def test_extract_salary_range(self):
        """Test extract_salary_range function."""
        text = "Salary: $50k per year"
        result = extract_salary_range(text)
        
        assert result is not None
        assert result['is_range'] is False
        assert result['min_amount'] == 50000.0
        assert result['currency'] == 'USD'
        assert result['period'] == 'yearly'
    
    def test_extract_salary_range_no_salary(self):
        """Test extract_salary_range when no salary is found."""
        text = "We're looking for a developer"
        result = extract_salary_range(text)
        
        assert result is None

class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_text(self):
        """Test handling of empty text."""
        extractor = SalaryExtractor()
        result = extractor.extract_salaries("")
        assert result == []
        
        result = extractor.extract_salaries(None)
        assert result == []
    
    def test_malformed_patterns(self):
        """Test handling of malformed salary patterns."""
        text = "Salary: $abc, £def, €ghi"
        extractor = SalaryExtractor()
        result = extractor.extract_salaries(text)
        
        # Should handle gracefully without crashing
        assert isinstance(result, list)
    
    def test_very_large_numbers(self):
        """Test handling of very large salary numbers."""
        text = "Salary: $999999999999999"
        extractor = SalaryExtractor()
        result = extractor.extract_salaries(text)
        
        assert len(result) > 0
        assert result[0].min_amount == Decimal('999999999999999')
    
    def test_mixed_currencies(self):
        """Test handling of mixed currencies in same text."""
        text = "Salary: $50k USD or £40k GBP"
        extractor = SalaryExtractor()
        result = extractor.extract_salaries(text)
        
        assert len(result) >= 2
        currencies = [s.currency for s in result]
        assert 'USD' in currencies
        assert 'GBP' in currencies

class TestRealWorldExamples:
    """Test with real-world job posting examples."""
    
    def test_real_job_posting_1(self):
        """Test with a realistic job posting."""
        text = """
        🚀 Junior Python Developer Wanted!
        
        We're looking for a talented junior developer to join our remote team.
        Requirements:
        - Python experience
        - React knowledge
        - AWS familiarity
        - Remote work capability
        
        Salary: £45,000 - £55,000 per annum
        Location: Remote (UK-based)
        """
        
        extractor = SalaryExtractor()
        result = extractor.extract_salaries(text)
        
        assert len(result) > 0
        salary = result[0]
        assert salary.is_range is True
        assert salary.min_amount == Decimal('45000')
        assert salary.max_amount == Decimal('55000')
        assert salary.currency == 'GBP'
        assert salary.period == 'yearly'
    
    def test_real_job_posting_2(self):
        """Test with another realistic job posting."""
        text = """
        Senior React Developer
        
        We need a senior React developer for our team.
        - 5+ years experience
        - React, TypeScript, Node.js
        - Remote work available
        
        Compensation: $120k - $150k USD annually
        Benefits: Health, dental, 401k
        """
        
        extractor = SalaryExtractor()
        result = extractor.extract_salaries(text)
        
        assert len(result) > 0
        salary = result[0]
        assert salary.is_range is True
        assert salary.min_amount == Decimal('120000')
        assert salary.max_amount == Decimal('150000')
        assert salary.currency == 'USD'
        assert salary.period == 'yearly'
    
    def test_russian_job_posting(self):
        """Test with Russian job posting."""
        text = """
        Требуется Python разработчик
        
        Мы ищем Python разработчика для удаленной работы.
        Требования:
        - Опыт работы с Python
        - Знание Django/Flask
        - Удаленная работа
        
        Зарплата: от 150000 до 250000 рублей
        """
        
        extractor = SalaryExtractor()
        result = extractor.extract_salaries(text)
        
        assert len(result) > 0
        salary = result[0]
        assert salary.is_range is True
        assert salary.min_amount == Decimal('150000')
        assert salary.max_amount == Decimal('250000')
        assert salary.currency == 'RUB'

if __name__ == '__main__':
    pytest.main([__file__]) 