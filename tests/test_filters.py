import pytest
from datetime import datetime, timedelta
import sys
import os
from decimal import Decimal

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from filters import MessageFilter, AdvancedFilter, RussianJobFilter

class TestMessageFilter:
    """Test cases for MessageFilter class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.keywords = ['python', 'react', 'remote', 'junior']
        self.filter = MessageFilter(self.keywords, date_filter_hours=24)
    
    def test_matches_keywords_positive(self):
        """Test keyword matching with positive cases"""
        test_cases = [
            "We're looking for a Python developer",
            "React frontend developer needed",
            "Remote work opportunity",
            "Junior developer position"
        ]
        
        for text in test_cases:
            assert self.filter.matches_keywords(text) == True
    
    def test_matches_keywords_negative(self):
        """Test keyword matching with negative cases"""
        test_cases = [
            "We're looking for a Java developer",
            "Angular frontend developer needed",
            "Office work only",
            "Senior developer position"
        ]
        
        for text in test_cases:
            assert self.filter.matches_keywords(text) == False
    
    def test_matches_keywords_case_insensitive(self):
        """Test that keyword matching is case insensitive"""
        test_cases = [
            "PYTHON developer",
            "React DEVELOPER",
            "REMOTE work",
            "JUNIOR position"
        ]
        
        for text in test_cases:
            assert self.filter.matches_keywords(text) == True
    
    def test_matches_date_filter_recent(self):
        """Test date filtering with recent messages"""
        recent_date = datetime.now() - timedelta(hours=12)
        assert self.filter.matches_date_filter(recent_date) == True
    
    def test_matches_date_filter_old(self):
        """Test date filtering with old messages"""
        old_date = datetime.now() - timedelta(hours=48)
        assert self.filter.matches_date_filter(old_date) == False
    
    def test_matches_date_filter_no_filter(self):
        """Test date filtering when no filter is set"""
        filter_no_date = MessageFilter(self.keywords, date_filter_hours=0)
        old_date = datetime.now() - timedelta(days=30)
        assert filter_no_date.matches_date_filter(old_date) == True
    
    def test_filter_message_complete(self):
        """Test complete message filtering"""
        recent_message = {
            'message': 'We need a Python developer for remote work',
            'date': datetime.now() - timedelta(hours=6)
        }
        assert self.filter.filter_message(recent_message) == True
    
    def test_filter_message_old(self):
        """Test filtering old messages"""
        old_message = {
            'message': 'We need a Python developer for remote work',
            'date': datetime.now() - timedelta(hours=48)
        }
        assert self.filter.filter_message(old_message) == False
    
    def test_filter_message_no_keywords(self):
        """Test filtering messages without keywords"""
        recent_message = {
            'message': 'We need a Java developer for office work',
            'date': datetime.now() - timedelta(hours=6)
        }
        assert self.filter.filter_message(recent_message) == False
    
    def test_get_matched_keywords(self):
        """Test getting matched keywords from text"""
        text = "We need a Python developer with React experience for remote work"
        matched = self.filter.get_matched_keywords(text)
        expected = ['python', 'react', 'remote']
        
        assert set(matched) == set(expected)
    
    def test_extract_message_text(self):
        """Test message text extraction"""
        message = {'message': 'Test message'}
        assert self.filter._extract_message_text(message) == 'Test message'
        
        message = {'text': 'Test text'}
        assert self.filter._extract_message_text(message) == 'Test text'
        
        message = {'caption': 'Test caption'}
        assert self.filter._extract_message_text(message) == 'Test caption'
        
        message = {}
        assert self.filter._extract_message_text(message) == ''

class TestAdvancedFilter:
    """Test cases for AdvancedFilter class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.keywords = ['python', 'react', 'remote']
        self.exclude_keywords = ['senior', 'lead']
        self.filter = AdvancedFilter(
            keywords=self.keywords,
            exclude_keywords=self.exclude_keywords,
            min_salary=30000,
            max_salary=80000
        )
    
    def test_exclude_keywords(self):
        """Test exclude keyword filtering"""
        # Should be excluded due to 'senior'
        message = {
            'message': 'We need a Python developer for remote work, senior level',
            'date': datetime.now() - timedelta(hours=6)
        }
        assert self.filter.filter_message(message) == False
        
        # Should pass (no exclude keywords)
        message = {
            'message': 'We need a Python developer for remote work',
            'date': datetime.now() - timedelta(hours=6)
        }
        assert self.filter.filter_message(message) == True
    
    def test_salary_range_matching(self):
        """Test salary range filtering"""
        # Salary within range
        text = "Python developer position, salary £50,000"
        assert self.filter._matches_salary_range(text) == True
        
        # Salary below minimum
        text = "Python developer position, salary £25,000"
        assert self.filter._matches_salary_range(text) == False
        
        # Salary above maximum
        text = "Python developer position, salary £90,000"
        assert self.filter._matches_salary_range(text) == False
        
        # No salary mentioned
        text = "Python developer position"
        assert self.filter._matches_salary_range(text) == True
    
    def test_salary_patterns(self):
        """Test different salary patterns"""
        test_cases = [
            ("£50k", True),
            ("£50,000", True),
            ("$60k", True),
            ("$60,000", True),
            ("€70k", True),
            ("70k pounds", True),
            ("50k dollars", True),
        ]
        
        for text, expected in test_cases:
            assert self.filter._matches_salary_range(f"Python developer, salary {text}") == expected
    
    def test_no_salary_filter(self):
        """Test when no salary filter is set"""
        filter_no_salary = AdvancedFilter(
            keywords=self.keywords,
            exclude_keywords=self.exclude_keywords
        )
        
        text = "Python developer position"
        assert filter_no_salary._matches_salary_range(text) == True

class TestFilterIntegration:
    """Integration tests for filtering"""
    
    def test_real_job_posting(self):
        """Test with realistic job posting text"""
        keywords = ['python', 'react', 'remote', 'junior', 'aws']
        filter_obj = MessageFilter(keywords, date_filter_hours=24)
        
        job_posting = {
            'message': '''
            🚀 Junior Python Developer Wanted!
            
            We're looking for a talented junior developer to join our remote team.
            Requirements:
            - Python experience
            - React knowledge
            - AWS familiarity
            - Remote work capability
            
            Salary: £45,000
            Location: Remote (UK-based)
            ''',
            'date': datetime.now() - timedelta(hours=2)
        }
        
        assert filter_obj.filter_message(job_posting) == True
        
        # Check matched keywords
        text = filter_obj._extract_message_text(job_posting)
        matched = filter_obj.get_matched_keywords(text)
        expected_keywords = ['python', 'react', 'remote', 'junior', 'aws']
        
        for keyword in expected_keywords:
            assert keyword in matched

class TestRussianJobFilter:
    """Test cases for RussianJobFilter class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.keywords = ['python', 'react', 'remote', 'junior']
        self.filter = RussianJobFilter(self.keywords, date_filter_hours=24)
    
    def test_junior_keywords_positive(self):
        """Test that junior keywords are accepted"""
        test_cases = [
            "Junior Python developer needed",
            "Джуниор разработчик Python",
            "Intern position available",
            "Стажер Python разработчик",
            "Entry level developer",
            "Начальный уровень разработки"
        ]
        
        for text in test_cases:
            message = {
                'message': text,
                'date': datetime.now() - timedelta(hours=6)
            }
            assert self.filter.filter_message(message) == True
    
    def test_senior_keywords_negative(self):
        """Test that senior keywords are excluded"""
        test_cases = [
            "Senior Python developer needed",
            "Сеньор разработчик Python",
            "Lead developer position",
            "Team lead Python",
            "Principal developer",
            "Архитектор системы"
        ]
        
        for text in test_cases:
            message = {
                'message': text,
                'date': datetime.now() - timedelta(hours=6)
            }
            assert self.filter.filter_message(message) == False
    
    def test_experience_requirements(self):
        """Test experience requirement filtering"""
        # Should pass (junior keyword present)
        message = {
            'message': "Junior Python developer with 1 year experience",
            'date': datetime.now() - timedelta(hours=6)
        }
        assert self.filter.filter_message(message) == True
        
        # Should pass (low experience)
        message = {
            'message': "Python developer with 2 years experience",
            'date': datetime.now() - timedelta(hours=6)
        }
        assert self.filter.filter_message(message) == True
        
        # Should fail (high experience)
        message = {
            'message': "Python developer with 5 years experience",
            'date': datetime.now() - timedelta(hours=6)
        }
        assert self.filter.filter_message(message) == False
    
    def test_remote_requirement(self):
        """Test remote work requirement"""
        # Should fail (no remote mentioned)
        message = {
            'message': "Junior Python developer for office work",
            'date': datetime.now() - timedelta(hours=6)
        }
        assert self.filter.filter_message(message) == False
        
        # Should pass (remote mentioned)
        message = {
            'message': "Junior Python developer for remote work",
            'date': datetime.now() - timedelta(hours=6)
        }
        assert self.filter.filter_message(message) == True
    
    def test_complete_filtering(self):
        """Test complete filtering with all requirements"""
        # Perfect match
        message = {
            'message': "Junior Python developer for remote work, 1 year experience",
            'date': datetime.now() - timedelta(hours=6)
        }
        assert self.filter.filter_message(message) == True
        
        # Missing remote
        message = {
            'message': "Junior Python developer for office work, 1 year experience",
            'date': datetime.now() - timedelta(hours=6)
        }
        assert self.filter.filter_message(message) == False
        
        # Too much experience
        message = {
            'message': "Junior Python developer for remote work, 5 years experience",
            'date': datetime.now() - timedelta(hours=6)
        }
        assert self.filter.filter_message(message) == False
    
    def test_get_experience_info(self):
        """Test experience information extraction"""
        text = "Junior Python developer with 2 years experience for remote work"
        info = self.filter.get_experience_info(text)
        
        assert info['is_junior'] == True
        assert info['experience_years'] == 2
        assert info['is_remote'] == True
        assert info['meets_requirements'] == True
    
    def test_get_salary_info(self):
        """Test salary information extraction"""
        text = "Junior Python developer, salary $50k-$80k USD for remote work"
        info = self.filter.get_salary_info(text)
        
        assert info['salaries_found'] == True
        assert info['salary_count'] > 0
        assert info['primary_salary'] is not None
        assert info['primary_salary']['currency'] == 'USD'
    
    def test_get_job_analysis(self):
        """Test comprehensive job analysis"""
        text = "Junior Python developer with 1 year experience, salary $50k, remote work"
        analysis = self.filter.get_job_analysis(text)
        
        assert 'experience' in analysis
        assert 'salary' in analysis
        assert 'matched_keywords' in analysis
        assert 'excluded_keywords' in analysis
        assert analysis['remote_work_mentioned'] == True
        assert analysis['junior_position'] == True
    
    def test_get_excluded_keywords(self):
        """Test excluded keywords extraction"""
        text = "Senior Python developer with 5 years experience"
        excluded = self.filter._get_excluded_keywords(text)
        
        assert 'senior' in excluded
        assert len(excluded) > 0

class TestEnhancedSalaryFiltering:
    """Test enhanced salary filtering capabilities"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.filter = AdvancedFilter(
            keywords=['python', 'developer'],
            min_salary=40000,
            max_salary=100000
        )
    
    def test_salary_range_filtering(self):
        """Test salary range filtering with enhanced extraction"""
        # Should pass (salary in range)
        message = {
            'message': "Python developer, salary $50k USD",
            'date': datetime.now() - timedelta(hours=6)
        }
        assert self.filter.filter_message(message) == True
        
        # Should fail (salary too low)
        message = {
            'message': "Python developer, salary $30k USD",
            'date': datetime.now() - timedelta(hours=6)
        }
        assert self.filter.filter_message(message) == False
        
        # Should fail (salary too high)
        message = {
            'message': "Python developer, salary $120k USD",
            'date': datetime.now() - timedelta(hours=6)
        }
        assert self.filter.filter_message(message) == False
    
    def test_different_currencies(self):
        """Test salary filtering with different currencies"""
        # GBP salary (should pass if conversion is implemented)
        message = {
            'message': "Python developer, salary £40k GBP",
            'date': datetime.now() - timedelta(hours=6)
        }
        # Note: This will pass because currency conversion is simplified
        assert self.filter.filter_message(message) == True
    
    def test_salary_ranges(self):
        """Test salary range extraction"""
        message = {
            'message': "Python developer, salary $50k-$80k USD",
            'date': datetime.now() - timedelta(hours=6)
        }
        assert self.filter.filter_message(message) == True
    
    def test_no_salary_filter(self):
        """Test when no salary filter is set"""
        filter_no_salary = AdvancedFilter(
            keywords=['python', 'developer']
        )
        
        message = {
            'message': "Python developer position",
            'date': datetime.now() - timedelta(hours=6)
        }
        assert filter_no_salary.filter_message(message) == True

if __name__ == '__main__':
    pytest.main([__file__])