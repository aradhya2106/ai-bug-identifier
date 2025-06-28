from flask import Flask, request, jsonify
import google.generativeai as genai
import json
import re
from typing import Dict, Any
from functools import wraps
import time
from collections import defaultdict

# Initialize Flask app FIRST
app = Flask(__name__)

# Simple rate limiting storage
request_counts = defaultdict(list)
RATE_LIMIT_REQUESTS = 10  # requests per minute
RATE_LIMIT_WINDOW = 60    # seconds

# Configure Google Gemini API
GEMINI_API_KEY = "AIzaSyBAGZQmc438MahNVV8g2RIsU7NpT7Xvchs"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Sample cases for testing
SAMPLE_CASES = [
    {
        "language": "python",
        "code": "def is_even(n):\n    return n % 2 == 1",
        "bug_type": "Logical Bug",
        "description": "Function returns True for odd numbers instead of even numbers",
        "suggestion": "Change condition to n % 2 == 0"
    },
    {
        "language": "python", 
        "code": "def divide(x, y):\n    return x / y",
        "bug_type": "Runtime Bug",
        "description": "Division by zero will cause ZeroDivisionError",
        "suggestion": "Add check: if y == 0: return None or handle the exception"
    },
    {
        "language": "python",
        "code": "for i in range(1, len(arr)):\n    print(arr[i])",
        "bug_type": "Off-by-one Bug", 
        "description": "Skips the first element (index 0) of the array",
        "suggestion": "Change to range(len(arr)) to include all elements"
    },
    {
        "language": "python",
        "code": "if not arr:\n    process(arr)",
        "bug_type": "Logic Bug",
        "description": "Processes empty array when it should skip it",
        "suggestion": "Change condition to if arr: to process only non-empty arrays"
    },
    {
        "language": "javascript",
        "code": "function factorial(n) {\n    if (n = 0) return 1;\n    return n * factorial(n - 1);\n}",
        "bug_type": "Logic Bug",
        "description": "Uses assignment (=) instead of comparison (===) in condition",
        "suggestion": "Change n = 0 to n === 0"
    }
]

def rate_limit(f):
    """Simple rate limiting decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        now = time.time()
        
        # Clean old requests outside the window
        request_counts[client_ip] = [
            req_time for req_time in request_counts[client_ip] 
            if now - req_time < RATE_LIMIT_WINDOW
        ]
        
        # Check if rate limit exceeded
        if len(request_counts[client_ip]) >= RATE_LIMIT_REQUESTS:
            return jsonify({
                "error": "Rate limit exceeded. Please try again later.",
                "retry_after": 60
            }), 429
            
        # Add current request
        request_counts[client_ip].append(now)
        
        return f(*args, **kwargs)
    return decorated_function

def is_valid_syntax(code: str, language: str) -> bool:
    """Check if code has basic syntax validity"""
    if language.lower() == "python":
        try:
            compile(code, '<string>', 'exec')
            return True
        except SyntaxError:
            return False
    elif language.lower() == "javascript":
        # Basic JS syntax check - look for common syntax errors
        if '=' in code and not ('==' in code or '===' in code):
            # Check for the assignment in conditions
            lines = code.split('\n')
            for line in lines:
                if 'if' in line and '=' in line and not ('==' in line or '===' in line):
                    return True  # passing to catch the logic error
        return True
    return True  # For other languages

def create_bug_finding_prompt(code: str, language: str, mode: str = "developer-friendly") -> str:
    """Create a structured prompt for the LLM to find bugs"""
    
    tone_instruction = {
        "developer-friendly": "Use clear, technical language that a developer would understand.",
        "casual": "Use friendly, conversational language like you're helping a friend."
    }.get(mode, "Use clear, technical language that a developer would understand.")
    
    prompt = f"""
You are an expert code reviewer. Analyze this {language} code snippet for bugs.

Code to analyze:
```{language}
{code}
```

Instructions:
- Look for these bug types: Logic Bug, Runtime Bug, Edge-case Bug, Off-by-one Bug
- {tone_instruction}
- Focus on functional correctness, not style

Respond with ONLY a JSON object in this exact format:
{{
    "bug_type": "one of: Logic Bug, Runtime Bug, Edge-case Bug, Off-by-one Bug, or No Bug Found",
    "description": "clear explanation of what's wrong",
    "suggestion": "specific fix recommendation"
}}

If no bugs found, use "No Bug Found" as bug_type and explain why the code looks correct.
"""
    return prompt

def parse_llm_response(response_text: str) -> Dict[str, str]:
    """Parse LLM response and extract JSON"""
    try:
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            return json.loads(json_str)
        else:
            # Fallback if no JSON found
            return {
                "bug_type": "Analysis Error",
                "description": "Could not parse AI response",
                "suggestion": "Please try again with a different code snippet"
            }
    except json.JSONDecodeError:
        return {
            "bug_type": "Analysis Error", 
            "description": "AI response was not valid JSON",
            "suggestion": "Please try again"
        }

# ROOT ROUTE - Must come AFTER app initialization
@app.route('/', methods=['GET'])
def home():
    """Root endpoint - API documentation"""
    return jsonify({
        "message": "AI-Powered Bug Identifier API",
        "version": "1.0",
        "assessment": "Zerotrail SDE Intern Assessment",
        "endpoints": {
            "POST /find-bug": "Analyze code snippets for bugs",
            "GET /sample-cases": "Get sample buggy code examples", 
            "GET /health": "Health check"
        },
        "usage": {
            "find_bug_example": {
                "url": "/find-bug",
                "method": "POST",
                "body": {
                    "language": "python",
                    "code": "def is_even(n): return n % 2 == 1"
                }
            }
        },
        "status": "API is running successfully! "
    })

@app.route('/find-bug', methods=['POST'])
@rate_limit
def find_bug():
    """Main endpoint to find bugs in code snippets"""
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No JSON data provided"
            }), 400
            
        # Validate required fields
        if 'code' not in data or 'language' not in data:
            return jsonify({
                "error": "Both 'code' and 'language' fields are required"
            }), 400
            
        code = data['code'].strip()
        language = data['language'].lower()
        mode = data.get('mode', 'developer-friendly')
        
        # Validate input
        if not code:
            return jsonify({
                "error": "Code cannot be empty"
            }), 400
            
        if len(code.split('\n')) > 30:
            return jsonify({
                "error": "Code snippet cannot exceed 30 lines"
            }), 400
            
        # Check for basic syntax errors
        if not is_valid_syntax(code, language):
            return jsonify({
                "language": language,
                "bug_type": "Syntax Error",
                "description": "The code contains syntax errors that prevent it from running",
                "suggestion": "Fix the syntax errors first, then resubmit for bug analysis"
            })
            
        # Create prompt and call AI
              # ── Create prompt and call Gemini ─────────────────────────
        prompt = create_bug_finding_prompt(code, language, mode)

        try:
            response = model.generate_content(prompt)
            bug_info = parse_llm_response(response.text)
        except Exception as e:                   # quota/network failure
            app.logger.warning(f"LLM error: {e}")
            bug_info = {
                "bug_type": "Analysis Error",
                "description": "LLM quota exceeded or API error. Fallback response.",
                "suggestion": "Try again later or make sure your API key has quota."
            }

        # include language in every response
        bug_info["language"] = language
        return jsonify(bug_info)

    except Exception as e:
        return jsonify({
            "error": f"Internal server error: {str(e)}"
        }), 500

@app.route('/sample-cases', methods=['GET'])
def get_sample_cases():
    """Bonus endpoint: return sample buggy code snippets"""
    return jsonify({
        "samples": SAMPLE_CASES,
        "count": len(SAMPLE_CASES)
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Bug Identifier API"
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found"
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "error": "Method not allowed"
    }), 405

if __name__ == '__main__':
    print("Bug Identifier API starting...")
    print("Endpoints available:")
    print("   GET  /                - API documentation") 
    print("   POST /find-bug        - Analyze code for bugs")
    print("   GET  /sample-cases    - Sample bug cases")
    print("   GET  /health          - Health check")
    print(" Access at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)