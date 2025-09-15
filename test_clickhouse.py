#!/usr/bin/env python3
"""
Test ClickHouse connection script
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_direct_weather_create():
    """Test trực tiếp tạo weather record"""
    print("🧪 Testing direct weather creation...")
    
    payload = {
        "location": "Test Location",
        "temperature": 25.0,
        "humidity": 80,
        "pressure": 1013.25,
        "description": "Sunny",
        "wind_speed": 10.5,
        "wind_direction": "NE"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/weather/",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Direct weather creation successful!")
            print(f"   Created ID: {result.get('id')}")
            print(f"   Location: {result.get('location')}")
            return True
        else:
            print(f"❌ Direct creation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return False

def test_weather_list():
    """Test lấy danh sách weather records"""
    print("\n📋 Testing weather list...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/weather/?limit=5")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Weather list retrieved!")
            print(f"   Found {len(result)} records")
            for i, record in enumerate(result[:2]):  # Show first 2
                print(f"   {i+1}. {record.get('location')} - {record.get('temperature')}°C")
            return len(result) > 0
        else:
            print(f"❌ List failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return False

def main():
    """Main test function"""
    print("🔧 ClickHouse Connection Test")
    print("=" * 40)
    
    # Test 1: Direct weather creation
    creation_success = test_direct_weather_create()
    
    # Test 2: List existing records
    list_success = test_weather_list()
    
    print("\n" + "=" * 40)
    if creation_success:
        print("✅ ClickHouse connection and insertion works!")
        print("🔍 Issue might be in WeatherAPI data conversion.")
    else:
        print("❌ ClickHouse connection or table creation issue.")
        print("🔍 Check ClickHouse logs and table structure.")
    
    if list_success:
        print("✅ Data retrieval works!")
    else:
        print("❌ Data retrieval issue.")

if __name__ == "__main__":
    main()
