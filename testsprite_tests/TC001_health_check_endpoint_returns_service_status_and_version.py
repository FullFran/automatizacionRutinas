import requests

def test_health_check_returns_status_and_version():
    url = "http://localhost:8000/health"
    headers = {
        "Accept": "application/json"
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        assert False, f"Request to {url} failed: {e}"

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    try:
        data = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"

    assert "status" in data, "Response JSON missing 'status' field"
    assert isinstance(data["status"], str), "'status' field is not a string"

    assert "version" in data, "Response JSON missing 'version' field"
    assert isinstance(data["version"], str), "'version' field is not a string"

test_health_check_returns_status_and_version()