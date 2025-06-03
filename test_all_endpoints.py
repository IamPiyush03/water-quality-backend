import requests
import json
from typing import Dict, Any
import os
from dotenv import load_dotenv
import subprocess
import time

# Load environment variables
load_dotenv()

BASE_URL = "http://localhost:8000"

# def setup_database():
#     """Initialize the database"""
#     try:
#         subprocess.run(["python", "create_db.py"], check=True)
#         subprocess.run(["python", "init_db.py"], check=True)
#         print("✅ Database initialized successfully")
#     except subprocess.CalledProcessError as e:
#         print(f"❌ Database initialization failed: {str(e)}")
#         raise

def test_health_check():
    """Test the health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
    print("✅ Health check endpoint test passed")

def test_predict_endpoint():
    """Test the prediction endpoint"""
    data = {
        "location": "Test Location",
        "Lat": 32.244947,
        "Lon": 77.19108,
        "Temperature": 9.0,
        "D_O": 9.0,
        "pH": 8.0,
        "Conductivity": 85,
        "B_O_D": 0.1,
        "Nitrate": 0.0,
        "Fecalcaliform": 0,
        "Totalcaliform": 0
    }
    
    response = requests.post(f"{BASE_URL}/predict", json=data)
    assert response.status_code == 200
    result = response.json()
    assert "measurement" in result
    assert "prediction" in result
    assert "recommendations" in result
    print("✅ Prediction endpoint test passed")
    return result["measurement"]["id"]

def test_get_measurement(measurement_id: int):
    """Test getting measurement details"""
    response = requests.get(f"{BASE_URL}/measurements/{measurement_id}")
    assert response.status_code == 200
    result = response.json()
    assert "measurement" in result
    assert "prediction" in result
    assert "recommendations" in result
    print("✅ Get measurement endpoint test passed")

def test_trends_endpoint():
    """Test the trends endpoint"""
    response = requests.get(f"{BASE_URL}/trends/Test%20Location")
    assert response.status_code == 200
    result = response.json()
    assert isinstance(result, dict)
    print("✅ Trends endpoint test passed")

def test_dashboard_endpoint():
    """Test the dashboard endpoint"""
    response = requests.get(f"{BASE_URL}/dashboard/Test%20Location")
    assert response.status_code == 200
    result = response.json()
    assert isinstance(result, dict)
    print("✅ Dashboard endpoint test passed")

def test_parameter_dashboard():
    """Test the parameter dashboard endpoint"""
    response = requests.get(f"{BASE_URL}/dashboard/Test%20Location/parameter/pH")
    assert response.status_code == 200
    result = response.json()
    assert isinstance(result, dict)
    print("✅ Parameter dashboard endpoint test passed")

def test_comparison_dashboard():
    """Test the comparison dashboard endpoint"""
    response = requests.get(f"{BASE_URL}/dashboard/compare?locations=Test%20Location,Test%20Location%202")
    assert response.status_code == 200
    result = response.json()
    assert isinstance(result, dict)
    print("✅ Comparison dashboard endpoint test passed")

def test_export_data():
    """Test the export data endpoint"""
    response = requests.get(f"{BASE_URL}/export/Test%20Location?format=csv")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv"
    print("✅ Export data endpoint test passed")

def run_all_tests():
    """Run all API tests"""
    print("Starting API tests...")
    
    try:
        # Wait for the server to be ready
        time.sleep(2)
        
        # Test health check
        test_health_check()
        
        # Test prediction and get measurement
        measurement_id = test_predict_endpoint()
        test_get_measurement(measurement_id)
        
        # Test trends and dashboard endpoints
        test_trends_endpoint()
        test_dashboard_endpoint()
        test_parameter_dashboard()
        test_comparison_dashboard()
        
        # Test export functionality
        test_export_data()
        
        print("\n🎉 All tests completed successfully!")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {str(e)}")
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to the API server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")

if __name__ == "__main__":
    run_all_tests() 