import requests
import json

# Test the API locally
BASE_URL = "http://localhost:5000"

def test_find_bug():
    """Test the main bug finding endpoint"""
    
    # Test case 1: Logical bug
    test_data_1 = {
        "language": "python",
        "code": "def is_even(n):\n    return n % 2 == 1"
    }
    
    print("Test 1: Logical Bug")
    response = requests.post(f"{BASE_URL}/find-bug", json=test_data_1)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)
    
    # Test case 2: Runtime bug
    test_data_2 = {
        "language": "python", 
        "code": "def divide(x, y):\n    return x / y"
    }
    
    print("Test 2: Runtime Bug")
    response = requests.post(f"{BASE_URL}/find-bug", json=test_data_2)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)
    
    # Test case 3: Off-by-one bug
    test_data_3 = {
        "language": "python",
        "code": "for i in range(1, len(arr)):\n    print(arr[i])"
    }
    
    print("Test 3: Off-by-one Bug")
    response = requests.post(f"{BASE_URL}/find-bug", json=test_data_3)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)
    
    # Test case 4: Edge case bug
    test_data_4 = {
        "language": "python",
        "code": "if not arr:\n    process(arr)"
    }
    
    print("Test 4: Edge Case Bug")
    response = requests.post(f"{BASE_URL}/find-bug", json=test_data_4)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

def test_sample_cases():
    """Test the sample cases endpoint"""
    print("Test: Sample Cases")
    response = requests.get(f"{BASE_URL}/sample-cases")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

def test_error_handling():
    """Test error handling"""
    print("Test: Error Handling")
    
    # Empty request
    response = requests.post(f"{BASE_URL}/find-bug", json={})
    print(f"Empty request - Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    
    # Missing code field
    response = requests.post(f"{BASE_URL}/find-bug", json={"language": "python"})
    print(f"Missing code - Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

if __name__ == "__main__":
    print("Testing Bug Identifier API")
    print("Make sure your API is running first!")
    print("=" * 50)
    
    try:
        test_find_bug()
        test_sample_cases() 
        test_error_handling()
        print("All tests completed")
    except requests.exceptions.ConnectionError:
        print("Could not connect to API. Make sure it's running on a localhost:5000")