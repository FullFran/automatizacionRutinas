import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_telegram_webhook_receives_and_processes_updates():
    url = f"{BASE_URL}/api/v1/telegram/webhook"
    headers = {
        "Content-Type": "application/json"
    }
    # Simulated Telegram update payload with a workout routine text message as would be sent to bot webhook
    payload = {
        "update_id": 10000,
        "message": {
            "message_id": 1365,
            "from": {
                "id": 123456789,
                "is_bot": False,
                "first_name": "TestUser",
                "username": "testuser",
                "language_code": "en"
            },
            "chat": {
                "id": 123456789,
                "first_name": "TestUser",
                "username": "testuser",
                "type": "private"
            },
            "date": 1618321234,
            "text": "Monday: 3x10 push-ups, 3x15 squats; Tuesday: 5x5 pull-ups"
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
        assert response.status_code == 200, f"Expected HTTP 200, got {response.status_code}"
        
        # As per PRD, no explicit response schema is required,
        # but ensure response content-type is JSON or empty (if no content)
        content_type = response.headers.get("Content-Type", "")
        # Accept either empty body or JSON response
        if response.content:
            assert "application/json" in content_type, "Response content-type is not application/json"
            # Optionally parse json to ensure no error
            json_response = response.json()
            # No specific fields required, just check it's a dict or empty dict
            assert isinstance(json_response, dict), "Response JSON is not a dictionary"
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

test_telegram_webhook_receives_and_processes_updates()