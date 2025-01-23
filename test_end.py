import requests
from datetime import datetime, timedelta

# Base URL - Change this according to your environment
BASE_URL = "http://localhost:8080"  # Local development
# BASE_URL = "https://gen-travel-685322644106.asia-south2.run.app"  # Production

def test_health():
    """Test the health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print("\nHealth Check Response:", response.json())
    
def test_test_endpoint():
    """Test the test endpoint"""
    response = requests.get(f"{BASE_URL}/test")
    print("\nTest Endpoint Response:", response.json())

def test_generate_itinerary():
    """Test the generate-itinerary endpoint"""
    # Calculate dates for a week-long trip starting next year
    start_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=371)).strftime("%Y-%m-%d")
    
    payload = {
        "destination": "Paris",
        "start_date": start_date,
        "end_date": end_date,
        "budget_level": "moderate"  # Can be "budget", "moderate", or "luxury"
    }
    
    response = requests.post(f"{BASE_URL}/generate-itinerary", json=payload)
    print("\nItinerary Generation Response:", response.json())

def test_chat():
    """Test the chat endpoint with formatted prompt"""
    system_prompt = "You are a helpful travel assistant."
    user_input = "Can you suggest a nice place to visit in Paris?"
    context = "The user is planning a visit to Paris and prefers historical landmarks."

    # Create the formatted prompt
    formatted_prompt = f"{system_prompt}\n\nContext: {context}\n\nUser: {user_input}\n\nAssistant:"

    payload = {
        "message": formatted_prompt
    }

    response = requests.post(f"{BASE_URL}/chat", json=payload)
    print("\nChat Response:", response.json())


def run_all_tests():
    """Run all test functions"""
    print("Starting API Tests...")
    print("=" * 50)
    
    try:
        test_health()
        test_test_endpoint()
        test_generate_itinerary()
        test_chat()
        
        print("\nAll tests completed successfully!")
        
    except requests.exceptions.RequestException as e:
        print(f"\nError occurred during testing: {str(e)}")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
    
    print("=" * 50)

if __name__ == "__main__":
    run_all_tests() 