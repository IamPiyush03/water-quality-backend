import requests
import sys

def test_server():
    """Test if the backend server is running and accessible"""
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Server is running and accessible")
            print(f"Health check response: {response.json()}")
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            print(f"Response: {response.text}")
            
        # Test dashboard endpoint
        response = requests.get("http://localhost:8000/api/dashboard/location1")
        if response.status_code == 200:
            print("✅ Dashboard endpoint is working")
            print(f"Dashboard response: {response.json()}")
        else:
            print(f"❌ Dashboard endpoint returned status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running at http://localhost:8000")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error testing server: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    test_server() 