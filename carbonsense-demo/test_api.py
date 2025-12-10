"""
Test script for CarbonSense AI Model Performance API endpoints
Run this to verify the backend API is working correctly
"""

import requests
import json
import time
from datetime import datetime

# Base URL for the API (adjust if needed)
BASE_URL = "http://localhost:5000/api"

def test_endpoint(endpoint_name, url):
    """Test an API endpoint and display results"""
    print(f"\n{'='*50}")
    print(f"Testing: {endpoint_name}")
    print(f"URL: {url}")
    print(f"{'='*50}")
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS!")
            print(f"Response size: {len(json.dumps(data))} characters")
            
            # Display key information based on endpoint
            if 'model-performance' in url:
                print(f"Model Accuracy: {data.get('model_status', {}).get('accuracy', 'N/A')}%")
                print(f"Training Samples: {data.get('model_status', {}).get('training_samples', 'N/A'):,}")
                print(f"Health Status: {data.get('model_status', {}).get('health_status', 'N/A')}")
                
            elif 'training-data' in url:
                print(f"Total Records: {data.get('total_records', 'N/A'):,}")
                print(f"Sample Size: {data.get('sample_size', 'N/A')}")
                if data.get('data'):
                    print(f"First Record Fields: {list(data['data'][0].keys())}")
                    
            elif 'real-time-logs' in url:
                print(f"Log Entries: {len(data.get('logs', []))}")
                print(f"System Status: {data.get('system_status', 'N/A')}")
                if data.get('logs'):
                    print(f"Latest Log: {data['logs'][0].get('message', 'N/A')}")
                    
            else:
                # Generic display for other endpoints
                if isinstance(data, dict):
                    print(f"Response Keys: {list(data.keys())}")
                else:
                    print(f"Response Type: {type(data)}")
            
        else:
            print(f"❌ FAILED! Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION FAILED! Is the Flask server running?")
        print("   Start the server with: python backend/app.py")
        
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT! Server is taking too long to respond")
        
    except Exception as e:
        print(f"❌ ERROR! {str(e)}")

def main():
    """Main test function"""
    print("🧪 CarbonSense AI API Testing Suite")
    print(f"Testing at: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # List of endpoints to test
    endpoints = [
        ("Model Performance", f"{BASE_URL}/model-performance"),
        ("Training Data", f"{BASE_URL}/training-data"),
        ("Real-time Logs", f"{BASE_URL}/real-time-logs"),
        ("Model Diagnostics", f"{BASE_URL}/model-diagnostics"),
        ("Current Status", f"{BASE_URL}/status"),
        ("Daily Summary", f"{BASE_URL}/summary"),
        ("Recommendations", f"{BASE_URL}/recommendations"),
        ("Historical Trends", f"{BASE_URL}/trends")
    ]
    
    # Test each endpoint
    for name, url in endpoints:
        test_endpoint(name, url)
        time.sleep(1)  # Small delay between tests
    
    print(f"\n{'='*50}")
    print("🏁 Testing Complete!")
    print(f"{'='*50}")
    
    # Test the HTML page accessibility
    print("\n📄 Testing HTML Dashboard:")
    try:
        # Try to access the model performance HTML page
        html_url = "http://localhost:5000/frontend/model_performance.html"
        print(f"Dashboard URL: {html_url}")
        print("   Open this URL in your browser to view the dashboard")
        
        # Try a simple HEAD request to check if file exists
        import os
        html_path = os.path.join(os.path.dirname(__file__), 'frontend', 'model_performance.html')
        if os.path.exists(html_path):
            print("✅ HTML file exists and should be accessible")
        else:
            print("⚠️  HTML file not found at expected location")
            
    except Exception as e:
        print(f"⚠️  Could not verify HTML accessibility: {e}")

if __name__ == "__main__":
    main()
