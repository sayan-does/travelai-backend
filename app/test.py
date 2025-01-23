import requests

# Test generate-itinerary endpoint
url_itinerary = "https://gen-travel-685322644106.asia-south2.run.app/generate-itinerary"
payload_itinerary = {
    "destination": "Paris",
    "start_date": "2025-05-01",
    "end_date": "2025-05-07",
    "budget_level": "medium"
}
response_itinerary = requests.post(url_itinerary, json=payload_itinerary)
print("Itinerary Response:", response_itinerary.json())
