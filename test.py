import requests

response = requests.get(
    "http://127.0.0.1:8000/",
    json={"message": "Hello, world!"}
)
print(response.json())

response = requests.post(
    "http://127.0.0.1:8000/chat",
    json={"message": "Hello, how are you?"}
)
print(response.json())