import pytest
from datetime import datetime, timedelta
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from filters import MessageFilter, AdvancedFilter

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

if __name__ == '__main__':
    pytest.main([__file__])