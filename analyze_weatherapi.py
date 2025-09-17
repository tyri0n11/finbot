import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = "5f1c5216b5b947038ae151549251509"  # Your API key
BASE_URL = "http://api.weatherapi.com/v1"

def fetch_current_weather(location="Ho Chi Minh City"):
    """Fetch current weather response"""
    print(f"🌤️  Fetching CURRENT weather for: {location}")
    
    url = f"{BASE_URL}/current.json"
    params = {
        "key": API_KEY,
        "q": location,
        "aqi": "no"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        print("✅ Current weather response:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        return data
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def fetch_forecast_weather(location="Ho Chi Minh City", days=1):
    """Fetch forecast weather response"""
    print(f"\n🔮 Fetching FORECAST weather for: {location} ({days} days)")
    
    url = f"{BASE_URL}/forecast.json"
    params = {
        "key": API_KEY,
        "q": location,
        "days": days,
        "aqi": "no",
        "alerts": "no"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        print("✅ Forecast weather response:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        return data
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def analyze_response_structure(data, response_type="current"):
    """Analyze và in ra cấu trúc của response"""
    print(f"\n📋 ANALYZING {response_type.upper()} RESPONSE STRUCTURE:")
    print("=" * 60)
    
    if not data:
        print("❌ No data to analyze")
        return
    
    def print_structure(obj, prefix="", max_depth=3, current_depth=0):
        if current_depth > max_depth:
            print(f"{prefix}... (max depth reached)")
            return
            
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, dict):
                    print(f"{prefix}{key}: dict")
                    print_structure(value, prefix + "  ", max_depth, current_depth + 1)
                elif isinstance(value, list):
                    print(f"{prefix}{key}: list[{len(value)} items]")
                    if value and current_depth < max_depth:
                        print(f"{prefix}  [0]: {type(value[0]).__name__}")
                        if isinstance(value[0], dict):
                            print_structure(value[0], prefix + "    ", max_depth, current_depth + 1)
                else:
                    print(f"{prefix}{key}: {type(value).__name__} = {repr(value)}")
        elif isinstance(obj, list):
            print(f"{prefix}list[{len(obj)} items]")
            if obj:
                print_structure(obj[0], prefix + "  ", max_depth, current_depth + 1)
    
    print_structure(data)

def save_response_to_file(data, filename):
    """Save response to JSON file for reference"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved response to: {filename}")
    except Exception as e:
        print(f"❌ Error saving file: {e}")

def main():
    """Main analysis function"""
    print("🔍 WeatherAPI.com Response Analyzer")
    print("=" * 50)
    
    location = "Ho Chi Minh City"
    
    # Fetch and analyze current weather
    current_data = fetch_current_weather(location)
    if current_data:
        analyze_response_structure(current_data, "current")
        save_response_to_file(current_data, "current_weather_response.json")
    
    # Fetch and analyze forecast weather
    forecast_data = fetch_forecast_weather(location, days=2)
    if forecast_data:
        analyze_response_structure(forecast_data, "forecast")
        save_response_to_file(forecast_data, "forecast_weather_response.json")
    
    print("\n" + "=" * 50)
    print("📝 NEXT STEPS:")
    print("1. Check generated JSON files: current_weather_response.json, forecast_weather_response.json")
    print("2. Update Pydantic models based on actual response structure")
    print("3. Make sure all fields in models match the API response")
    print("4. Test again with corrected models")

if __name__ == "__main__":
    main()
