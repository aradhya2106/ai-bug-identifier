import requests
import time

print("Testing Rate Limiting - Making 11 requests ")
print("=" * 50)

for i in range(11):
    try:
        response = requests.post('http://localhost:5000/find-bug', 
                               json={'language': 'python', 'code': 'print(1)'})
        print(f"Request {i+1}: Status {response.status_code}")
        
        # If rate is limited (possibly) :(
        if response.status_code == 429:
            print(f"  Rate limited! Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request {i+1}: Error - {e}")
    
    # Small delay to see the pattern better :)
    time.sleep(0.1)

print("\nRate limit test completed!")