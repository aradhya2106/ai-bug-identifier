# ai-bug-identifier

Features

Smart Bug Detection: Identifies logic, runtime, syntax, and edge-case bugs
Multi-Language Support: Python, JavaScript, C, and more
Rate Limiting: 10 requests per minute for abuse prevention
Multiple Response Modes: Developer-friendly or casual explanations
Comprehensive Testing: Full unit test coverage
Professional Error Handling: Graceful handling of edge cases

🔧 API Endpoints
POST /find-bug
Analyze code snippets for potential bugs.
Request:
json{
  "language": "python",
  "code": "def is_even(n): return n % 2 == 1",
  "mode": "developer-friendly"
}
Response:
json{
  "bug_type": "Logic Bug",
  "description": "The function is meant to check if a number is even, but it incorrectly returns True for odd numbers.",
  "suggestion": "Use `n % 2 == 0` instead."
}
GET /sample-cases
Get sample buggy code snippets for testing.
GET /health
Health check endpoint.
🛠️ Installation & Setup
Prerequisites

Python 3.8+
Google Gemini API Key

1. Clone the Repository
bashgit clone https://github.com/aradhya2106/ai-bug-identifier.git
cd ai-bug-identifier
2. Create Virtual Environment
bashpython -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
3. Install Dependencies
bashpip install -r requirements.txt
4. Environment Setup
Create a .env file in the project root:
envGEMINI_API_KEY=your_api_key_here
FLASK_ENV=development
5. Run the Application
bashpython app.py
The API will be available at http://localhost:5000
🧪 Testing
Run All Tests
bash# Unit tests
python test_unit.py

# Rate limiting test
python test_rate_limit.py

# Assignment-specific test cases
python test_assignment_cases.py
Test Coverage

✅ 13 Unit tests covering all endpoints and error cases
✅ Rate limiting functionality
✅ All assignment required test cases
✅ Edge case handling

 Usage Examples
Basic Bug Detection
bashcurl -X POST http://localhost:5000/find-bug \
  -H "Content-Type: application/json" \
  -d '{
    "language": "python",
    "code": "for i in range(1, len(arr)):\n    print(arr[i])"
  }'
Casual Mode
bashcurl -X POST "http://localhost:5000/find-bug?mode=casual" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "python", 
    "code": "return x / y"
  }'
Get Sample Cases
bashcurl http://localhost:5000/sample-cases
Supported Bug Types

Logic Bugs: Incorrect program logic
Runtime Bugs: Potential runtime errors (division by zero, null pointer, etc.)
Edge-case Bugs: Issues with boundary conditions
Off-by-one Bugs: Array indexing errors
Syntax Errors: Basic syntax issues
