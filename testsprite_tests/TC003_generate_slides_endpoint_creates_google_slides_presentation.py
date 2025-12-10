import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30


def test_generate_slides_creates_presentation():
    url = f"{BASE_URL}/api/v1/routines/generate-slides"
    headers = {"Content-Type": "application/json"}

    # Corrected payload matching GenerateSlidesRequest -> DaySchema -> ExerciseSchema
    payload = {
        "days": [
            {
                "day_number": 1,
                "exercises": [
                    {"name": "Push Ups", "sets": "3", "reps": ["15"]},
                    {"name": "Squats", "sets": "4", "reps": ["20"]},
                ],
                "total_exercises": 2,
            }
        ]
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)

        # If call fails (e.g. 500 error from Mock/Real service), we print response text to debug
        if not response.ok:
            print(f"Request failed with status {response.status_code}")
            print(f"Response body: {response.text}")

        response.raise_for_status()
    except requests.RequestException as e:
        assert False, f"Request to generate slides failed: {e}"

    # Validate response code
    assert response.status_code == 200

    # Validate response content type
    content_type = response.headers.get("Content-Type", "")
    assert "application/json" in content_type

    response_json = response.json()

    # Validate expected keys in response (PresentationResponse schema: id, url)
    assert "url" in response_json, f"Response missing 'url'. Got: {response_json}"
    assert "id" in response_json, f"Response missing 'id'. Got: {response_json}"

    link = response_json["url"]

    # Simple validation: the link should be a non-empty string and look like a URL
    assert isinstance(link, str) and link.startswith("http"), (
        "Invalid presentation link returned"
    )


test_generate_slides_creates_presentation()
