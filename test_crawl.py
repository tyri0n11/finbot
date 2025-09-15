#!/usr/bin/env python3
"""
Script để test crawl weather data từ WeatherAPI.com
"""

import requests
import json
import time
from datetime import datetime

# Config
API_BASE_URL = "http://localhost:8000"
TEST_LOCATIONS = [
    "Ho Chi Minh City",
]

def test_health():
    """Test API health"""
    print("🔍 Testing API health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API is healthy!")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API not accessible: {e}")
        return False

def crawl_location(location, include_current=True, include_forecast=True, days=3):
    """Crawl weather data for a specific location"""
    print(f"\n📍 Crawling weather data for: {location}")
    
    payload = {
        "location": location,
        "include_current": include_current,
        "include_forecast": include_forecast,
        "days": days
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/automation/crawl",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(result)
            print(f"✅ Success: {result['message']}")
            print(f"   Records created: {result['records_created']}")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return False

def get_weather_data(location):
    """Get current weather data for display"""
    print(f"\n🌤️  Getting current weather for: {location}")
    
    try:
        response = requests.get(f"{API_BASE_URL}/n8n/weather/current/{location}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Weather data retrieved:")
            print(f"   Temperature: {result['current_temp']}°C")
            print(f"   Condition: {result['description']}")
            print(f"   Humidity: {result['humidity']}%")
            print(f"   Pressure: {result['pressure']} mb")
            if result['wind_speed']:
                print(f"   Wind: {result['wind_speed']} km/h {result['wind_direction'] or ''}")
            print(f"   Last Updated: {result['last_updated']}")
            return True
        else:
            print(f"❌ Failed to get weather data: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return False

def get_available_locations():
    """Get list of available locations"""
    print("\n📋 Getting available locations...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/n8n/locations")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Found {result['total']} locations:")
            for location in result['locations']:
                print(f"   - {location}")
            return result['locations']
        else:
            print(f"❌ Failed to get locations: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return []

def main():
    """Main test function"""
    print("🚀 Weather API Crawl Test Script")
    print("=" * 50)
    
    # Test 1: Health check
    if not test_health():
        print("❌ API is not available. Please check if containers are running.")
        return
    
    print("\n" + "=" * 50)
    print("📡 Starting crawl test...")
    
    # Test 2: Crawl data for test locations
    successful_crawls = 0
    for location in TEST_LOCATIONS:
        success = crawl_location(location, include_current=True, include_forecast=True, days=2)
        if success:
            successful_crawls += 1
        
        # Wait between requests to avoid overwhelming API
        time.sleep(2)
    
    print(f"\n📊 Crawl Summary: {successful_crawls}/{len(TEST_LOCATIONS)} locations successful")
    
    # Test 3: Verify data was stored
    print("\n" + "=" * 50)
    print("📊 Verifying stored data...")
    
    time.sleep(5)  # Wait for data to be processed
    
    stored_locations = get_available_locations()
    
    # Test 4: Get weather data for first successful location
    if stored_locations:
        test_location = stored_locations[0]
        get_weather_data(test_location)
        
        # Test forecast
        print(f"\n🔮 Getting forecast for: {test_location}")
        try:
            response = requests.get(f"{API_BASE_URL}/n8n/weather/forecast/{test_location}?days=3")
            if response.status_code == 200:
                result = response.json()
                print("✅ Forecast data retrieved:")
                print(f"   Forecast days: {result['forecast_days']}")
                for day in result['forecast_data'][:2]:  # Show first 2 days
                    print(f"   {day['date']}: {day['temperature']}°C - {day['description']}")
            else:
                print(f"❌ Failed to get forecast: {response.status_code}")
        except Exception as e:
            print(f"❌ Forecast error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Test completed!")
    
    if successful_crawls > 0:
        print("✅ Weather data successfully crawled and stored!")
        print("💡 You can now use these endpoints in N8N:")
        print(f"   - Crawl: POST {API_BASE_URL}/automation/crawl")
        print(f"   - Current: GET {API_BASE_URL}/n8n/weather/current/{{location}}")
        print(f"   - Forecast: GET {API_BASE_URL}/n8n/weather/forecast/{{location}}")
        print(f"   - Docs: {API_BASE_URL}/docs")
    else:
        print("❌ No data was successfully crawled. Check API logs for errors.")

if __name__ == "__main__":
    main()
