import requests

BASE_URL = "http://localhost:8000"
ENDPOINT = "/api/v1/routines/parse"
TIMEOUT = 30


def test_parse_routine_endpoint_parses_workout_text_into_structured_data():
    url = BASE_URL + ENDPOINT
    headers = {
        "Content-Type": "application/json"
    }
    # Example workout routine text that might be sent, based on typical input to an AI parsing endpoint
    payload = {
        "text": (
            "Monday: Chest\n"
            "- Bench Press 3 sets of 10 reps\n"
            "- Dumbbell Fly 3 sets of 12 reps\n"
            "Wednesday: Back\n"
            "- Pull Ups 4 sets to failure\n"
            "- Deadlifts 3 sets of 5 reps\n"
            "Friday: Legs\n"
            "- Squats 4 sets of 8 reps\n"
            "- Leg Press 3 sets of 10 reps"
        )
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request to {url} failed: {e}"

    # Validate HTTP status code
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    # Validate content-type header
    content_type = response.headers.get("Content-Type", "")
    assert "application/json" in content_type, f"Expected JSON response, got Content-Type: {content_type}"

    try:
        data = response.json()
    except ValueError:
        assert False, "Response body is not valid JSON"

    # Validate that the response is a dict/object
    assert isinstance(data, dict), "Response JSON is not an object"

    # Additional sanity check: response should not be empty
    assert len(data) > 0, "Response JSON is empty"


test_parse_routine_endpoint_parses_workout_text_into_structured_data()
