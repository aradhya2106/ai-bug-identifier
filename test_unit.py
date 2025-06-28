import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, parse_llm_response, create_bug_finding_prompt, is_valid_syntax

class TestBugIdentifierAPI(unittest.TestCase):
    
    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['service'], 'Bug Identifier API')
    
    def test_sample_cases_endpoint(self):
        """Test the sample cases endpoint"""
        response = self.app.get('/sample-cases')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('samples', data)
        self.assertIn('count', data)
        self.assertGreater(data['count'], 0)
    
    def test_find_bug_missing_fields(self):
        """Test find-bug endpoint with missing required fields"""
        # Test missing code fields
        response = self.app.post('/find-bug', 
                                json={'language': 'python'})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        
        
        response = self.app.post('/find-bug', 
                                json={'code': 'print("hello")'})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_find_bug_empty_code(self):
        """Test find-bug endpoint with empty code"""
        response = self.app.post('/find-bug', 
                                json={'language': 'python', 'code': ''})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_find_bug_too_long_code(self):
        """Test find-bug endpoint with code exceeding 30 lines"""
        long_code = '\n'.join([f'print({i})' for i in range(35)])
        response = self.app.post('/find-bug', 
                                json={'language': 'python', 'code': long_code})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('30 lines', data['error'])
    
    @patch('app.model.generate_content')
    def test_find_bug_with_mocked_llm(self, mock_generate):
        """Test find-bug endpoint with mocked LLM response"""
        # Mock the LLM response
        mock_response = MagicMock()
        mock_response.text = '''
        {
            "bug_type": "Logic Bug",
            "description": "The function returns True for odd numbers instead of even numbers",
            "suggestion": "Change condition to n % 2 == 0"
        }
        '''
        mock_generate.return_value = mock_response
        
        # Testing endpoint
        response = self.app.post('/find-bug', 
                                json={
                                    'language': 'python', 
                                    'code': 'def is_even(n):\n    return n % 2 == 1'
                                })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Check response str
        self.assertIn('bug_type', data)
        self.assertIn('description', data)
        self.assertIn('suggestion', data)
        self.assertIn('language', data)
        
        # Check values
        self.assertEqual(data['bug_type'], 'Logic Bug')
        self.assertEqual(data['language'], 'python')
        
        # Verify the LLM was called
        mock_generate.assert_called_once()
    
    @patch('app.model.generate_content')
    def test_find_bug_with_casual_mode(self, mock_generate):
        """Test find-bug endpoint with casual mode"""
        # Mock the LLM response
        mock_response = MagicMock()
        mock_response.text = '''
        {
            "bug_type": "Logic Bug",
            "description": "Hey! This function is backwards - it says numbers are even when they're actually odd!",
            "suggestion": "Just flip that condition to n % 2 == 0 and you're good to go!"
        }
        '''
        mock_generate.return_value = mock_response
        
        # Test with casual mode
        response = self.app.post('/find-bug', 
                                json={
                                    'language': 'python', 
                                    'code': 'def is_even(n):\n    return n % 2 == 1',
                                    'mode': 'casual'
                                })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['bug_type'], 'Logic Bug')
    
    def test_parse_llm_response_valid_json(self):
        """Test parsing valid JSON from LLM response"""
        response_text = '''
        Here's the analysis:
        {
            "bug_type": "Logic Bug",
            "description": "Test description",
            "suggestion": "Test suggestion"
        }
        Some additional text.
        '''
        
        result = parse_llm_response(response_text)
        self.assertEqual(result['bug_type'], 'Logic Bug')
        self.assertEqual(result['description'], 'Test description')
        self.assertEqual(result['suggestion'], 'Test suggestion')
    
    def test_parse_llm_response_invalid_json(self):
        """Test parsing invalid JSON from LLM response"""
        response_text = "This is not JSON at all!"
        
        result = parse_llm_response(response_text)
        self.assertEqual(result['bug_type'], 'Analysis Error')
        self.assertIn('Could not parse AI response', result['description'])
    
    def test_create_bug_finding_prompt(self):
        """Test prompt creation for different modes"""
        code = "def test(): pass"
        language = "python"
        
        
        prompt_dev = create_bug_finding_prompt(code, language, "developer-friendly")
        self.assertIn("technical language", prompt_dev)
        self.assertIn(code, prompt_dev)
        self.assertIn(language, prompt_dev)
        
        # Test casual mode
        prompt_casual = create_bug_finding_prompt(code, language, "casual")
        self.assertIn("friendly, conversational", prompt_casual)
        self.assertIn(code, prompt_casual)
    
    def test_is_valid_syntax(self):
        """Test syntax validation for different languages"""
        # Valid Python code
        self.assertTrue(is_valid_syntax("def test(): pass", "python"))
        
        # Invalid Python syntax
        self.assertFalse(is_valid_syntax("def test( pass", "python"))
        
        # JavaScript (basic check)
        self.assertTrue(is_valid_syntax("function test() { return true; }", "javascript"))
    
    def test_404_handler(self):
        """Test 404 error handler"""
        response = self.app.get('/nonexistent-endpoint')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('not found', data['error'].lower())
    
    def test_405_handler(self):
        """Test 405 method not allowed handler"""
        response = self.app.get('/find-bug')  # GET instead of POST
        self.assertEqual(response.status_code, 405)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('not allowed', data['error'].lower())

if __name__ == '__main__':
    print(" Running Unit Tests for Bug Identifier API")
    print("=" * 50)
    
    # Run the tests
    unittest.main(verbosity=2)
