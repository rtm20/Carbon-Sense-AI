"""
Quick API test script to verify the fixes
"""

import requests
import time

def test_endpoint_quick(name, url, timeout=5):
    """Quick test of an endpoint with timeout"""
    print(f"Testing {name}...", end=" ")
    try:
        start_time = time.time()
        response = requests.get(url, timeout=timeout)
        end_time = time.time()
        
        if response.status_code == 200:
            print(f"✅ SUCCESS ({end_time - start_time:.2f}s)")
            return True
        else:
            print(f"❌ FAILED! Status: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print(f"⏰ TIMEOUT!")
        return False
    except requests.exceptions.ConnectionError:
        print(f"🔌 CONNECTION FAILED!")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    base_url = "http://localhost:5000/api"
    
    print("🔧 Quick API Fix Verification")
    print("=" * 40)
    
    # Test the previously failing endpoints
    endpoints = [
        ("Real-time Logs", f"{base_url}/real-time-logs"),
        ("Summary", f"{base_url}/summary"),
        ("Recommendations", f"{base_url}/recommendations"),
        ("Trends", f"{base_url}/trends"),
        ("Model Performance", f"{base_url}/model-performance")
    ]
    
    success_count = 0
    for name, url in endpoints:
        if test_endpoint_quick(name, url):
            success_count += 1
        time.sleep(0.5)  # Small delay between tests
    
    print(f"\n📊 Results: {success_count}/{len(endpoints)} endpoints working")
    
    if success_count == len(endpoints):
        print("🎉 All endpoints are now working!")
        print("✅ You can now open the dashboard:")
        print("   http://localhost:5000/frontend/model_performance.html")
    else:
        print("⚠️  Some endpoints still need attention")

if __name__ == "__main__":
    main()
