import requests
import json

def debug_search():
    base_url = "https://linuxcmddb.preview.emergentagent.com/api"
    
    print("🔍 Debugging Search Endpoint...")
    
    # Test 1: Search with only category filter
    print("\n1. Testing category filter only:")
    response = requests.post(f"{base_url}/commands/search", 
                           json={"category": "Security", "limit": 3},
                           headers={"Content-Type": "application/json"})
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Found {len(data)} commands:")
        for cmd in data:
            print(f"   - {cmd['name']}: {cmd['category']}")
    else:
        print(f"   Error: {response.status_code} - {response.text}")
    
    # Test 2: Compare with GET endpoint
    print("\n2. Testing GET endpoint with same category:")
    response = requests.get(f"{base_url}/commands?category=Security&limit=3")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Found {len(data)} commands:")
        for cmd in data:
            print(f"   - {cmd['name']}: {cmd['category']}")
    else:
        print(f"   Error: {response.status_code} - {response.text}")
    
    # Test 3: Search with no filters (should return all)
    print("\n3. Testing search with no filters:")
    response = requests.post(f"{base_url}/commands/search", 
                           json={"limit": 3},
                           headers={"Content-Type": "application/json"})
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Found {len(data)} commands:")
        for cmd in data:
            print(f"   - {cmd['name']}: {cmd['category']}")
    else:
        print(f"   Error: {response.status_code} - {response.text}")
    
    # Test 4: Search with tag filter only
    print("\n4. Testing tag filter only:")
    response = requests.post(f"{base_url}/commands/search", 
                           json={"tags": ["security"], "limit": 3},
                           headers={"Content-Type": "application/json"})
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Found {len(data)} commands:")
        for cmd in data:
            print(f"   - {cmd['name']}: {cmd['category']} - tags: {cmd['tags'][:3]}...")
    else:
        print(f"   Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    debug_search()