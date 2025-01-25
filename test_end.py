import requests
from datetime import datetime, timedelta
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Base URL - Change this according to your environment
BASE_URL = "http://localhost:8080"  # Local development

# System prompt from LLMService
SYSTEM_PROMPT = """You are an expert AI travel assistant. Your role is to:
1. Create detailed, personalized travel itineraries
2. Provide accurate local information and recommendations
3. Consider budget constraints and preferences
4. Give practical travel tips and cultural insights
5. Maintain a friendly, professional tone

When generating itineraries:
- Include specific times for activities
- Provide realistic cost estimates in USD
- Consider local operating hours and seasonal factors
- Balance tourist attractions with local experiences
- Account for travel time between locations"""

def test_health():
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        logger.info(f"Health Check Response: {data}")
        print("✓ Health check passed")
        return True
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        print(f"✗ Health check failed: {str(e)}")
        return False

def test_test_endpoint():
    """Test the test endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/test")
        assert response.status_code == 200
        data = response.json()
        logger.info(f"Test Endpoint Response: {data}")
        print("✓ Test endpoint check passed")
        return True
    except Exception as e:
        logger.error(f"Test endpoint check failed: {str(e)}")
        print(f"✗ Test endpoint check failed: {str(e)}")
        return False

def test_generate_itinerary():
    """Test the generate-itinerary endpoint"""
    try:
        # Calculate dates for a 3-day trip starting next month
        start_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=32)).strftime("%Y-%m-%d")
        
        payload = {
            "destination": "Paris",
            "start_date": start_date,
            "end_date": end_date,
            "budget_level": "moderate"  # Using enum value from BudgetLevel
        }
        
        response = requests.post(f"{BASE_URL}/generate-itinerary", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        # Validate response structure
        assert "destination" in data
        assert "daily_plans" in data
        assert "total_cost_estimate" in data
        
        logger.info(f"Itinerary Generation Response: {json.dumps(data, indent=2)}")
        print("✓ Itinerary generation test passed")
        return data
    except Exception as e:
        logger.error(f"Itinerary generation test failed: {str(e)}")
        print(f"✗ Itinerary generation test failed: {str(e)}")
        return None

def test_chat():
    """Test the chat endpoint"""
    try:
        test_queries = [
            "What are the must-visit attractions in Paris?",
            "Can you suggest budget-friendly restaurants in Paris?",
            "What's the best time to visit the Eiffel Tower?"
        ]
        
        for query in test_queries:
            # Format the prompt with system context
            formatted_prompt = f"{SYSTEM_PROMPT}\n\nUser: {query}\n\nAssistant:"
            
            payload = {
                "message": formatted_prompt
            }
            
            response = requests.post(f"{BASE_URL}/chat", json=payload)
            assert response.status_code == 200
            
            data = response.json()
            assert "response" in data
            
            logger.info(f"Chat Query: {query}")
            logger.info(f"Response: {data['response'][:100]}...")  # First 100 chars
            
        print("✓ Chat test passed")
        return True
    except Exception as e:
        logger.error(f"Chat test failed: {str(e)}")
        print(f"✗ Chat test failed: {str(e)}")
        return False

def test_error_handling():
    """Test error handling with invalid inputs"""
    try:
        # Test with invalid date format
        payload = {
            "destination": "Paris",
            "start_date": "invalid-date",
            "end_date": "invalid-date",
            "budget_level": "moderate"
        }
        
        response = requests.post(f"{BASE_URL}/generate-itinerary", json=payload)
        assert response.status_code == 422  # Expecting validation error
        
        # Test with invalid budget level
        payload = {
            "destination": "Paris",
            "start_date": "2024-01-01",
            "end_date": "2024-01-02",
            "budget_level": "invalid"
        }
        
        response = requests.post(f"{BASE_URL}/generate-itinerary", json=payload)
        assert response.status_code == 422  # Expecting validation error
        
        print("✓ Error handling test passed")
        return True
    except Exception as e:
        logger.error(f"Error handling test failed: {str(e)}")
        print(f"✗ Error handling test failed: {str(e)}")
        return False

def run_all_tests():
    """Run all test functions"""
    print("\nStarting API Tests...")
    print("=" * 50)
    
    test_results = {
        "health_check": False,
        "test_endpoint": False,
        "itinerary_generation": False,
        "chat": False,
        "error_handling": False
    }
    
    try:
        # Run tests
        test_results["health_check"] = test_health()
        test_results["test_endpoint"] = test_test_endpoint()
        
        if test_results["health_check"]:
            itinerary_data = test_generate_itinerary()
            test_results["itinerary_generation"] = bool(itinerary_data)
            
            if test_results["itinerary_generation"]:
                test_results["chat"] = test_chat()
                test_results["error_handling"] = test_error_handling()
        
        # Print summary
        print("\nTest Summary:")
        print("-" * 30)
        for test_name, result in test_results.items():
            status = "✓ Passed" if result else "✗ Failed"
            print(f"{test_name}: {status}")
        
        # Calculate overall success
        success_rate = sum(1 for result in test_results.values() if result) / len(test_results) * 100
        print(f"\nOverall Success Rate: {success_rate:.1f}%")
        
    except requests.exceptions.ConnectionError:
        logger.error("Connection error: Unable to connect to the server")
        print("\n✗ Connection error: Unable to connect to the server")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"\n✗ Unexpected error: {str(e)}")
    
    print("=" * 50)

if __name__ == "__main__":
    run_all_tests()