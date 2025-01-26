import requests
import json
from datetime import date

# Base URL for the API
BASE_URL = "http://localhost:8080"  

def test_get_itinerary_prompt():
    """Test the get-itinerary-prompt endpoint"""
    print("\nTesting /get-itinerary-prompt endpoint...")
    
    url = f"{BASE_URL}/get-itinerary-prompt"
    
    # Test data
    params = {
        "destination": "Paris",
        "start_date": "2025-05-01",
        "end_date": "2025-05-07",
        "budget_level": "moderate"
    }
    
    try:
        response = requests.post(url, params=params)
        response.raise_for_status()
        
        result = response.json()
        print("✅ Successfully received prompt")
        print("Prompt preview:", result["prompt"][:1200] + "...")
        return result["prompt"]
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing get-itinerary-prompt: {str(e)}")
        if hasattr(e, 'response'):
            print("Error details:", e.response.text)
        raise

def test_get_itinerary(prompt: str):
    """Test the get-itinerary endpoint"""
    print("\nTesting /get-itinerary endpoint...")
    
    url = f"{BASE_URL}/get-itinerary"
    
    params = {
        "prompt": prompt
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        result = response.json()
        print("✅ Successfully generated itinerary")
        print("\nGenerated Itinerary:")
        print(json.dumps(result, indent=2))
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing get-itinerary: {str(e)}")
        if hasattr(e, 'response'):
            print("Error details:", e.response.text)
        raise

def main():
    print("Starting API tests...")
    try:
        # Test get-itinerary-prompt endpoint
        prompt = test_get_itinerary_prompt()
        print(type(prompt))
        
        # Test get-itinerary endpoint with the received prompt
        test_get_itinerary(prompt)
        
        print("\n✅ All tests passed successfully!")
        
    except Exception as e:
        print(f"\n❌ Tests failed: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()