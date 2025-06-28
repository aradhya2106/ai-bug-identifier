import requests
import json
import time

print("Testing Assignment Required Test Cases")
print("=" * 50)

# Test cases 
test_cases = [
    {
        "name": "Off-by-one bug",
        "code": "for i in range(1, len(arr)):\n    print(arr[i])",
        "language": "python"
    },
    {
        "name": "Division by zero",
        "code": "def divide(x, y):\n    return x / y",
        "language": "python"
    },
    {
        "name": "Assignment instead of comparison",
        "code": "if x = 5:\n    print('x is 5')",
        "language": "python"
    },
    {
        "name": "Logic error with empty check",
        "code": "if not arr:\n    process(arr)",
        "language": "python"
    }
]
for i, test_case in enumerate(test_cases, 1):
    try:
        print(f"\n🔍 Test Case {i}: {test_case['name']}")
        print(f"Code: {test_case['code']}")
        
        response = requests.post('http://localhost:5000/find-bug', 
                               json={
                                   'language': test_case['language'], 
                                   'code': test_case['code']
                               })
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Bug Type: {result.get('bug_type', 'N/A')}")
            print(f"Description: {result.get('description', 'N/A')}")
            print(f"Suggestion: {result.get('suggestion', 'N/A')}")
        else:
            print(f"Error: {response.text}")
            
        # Small delay between req
        time.sleep(1)
        
    except Exception as e:
        print(f"Error testing case {i}: {e}")

print("\nTest cases completed!")
