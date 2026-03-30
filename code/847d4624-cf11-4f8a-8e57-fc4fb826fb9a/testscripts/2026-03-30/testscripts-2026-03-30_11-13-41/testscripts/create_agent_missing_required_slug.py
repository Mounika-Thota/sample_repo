import pytest
import requests

# Constants (to be parameterized or managed securely in CI/CD)
BASE_URL = "https://api.example.com"  # Replace with actual base URL
API_ENDPOINT = "/api/agents/"
\****************(scope="module")
def auth_token():
    """
    Fixture to provide a valid Bearer token.
    In production, implement secure retrieval (e.g., from env or secrets manager).
    """
    # Placeholder: Replace with secure token retrieval
    token = "<REPLACE_WITH_TOKEN>"
    assert token and token != "<REPLACE_WITH_TOKEN>", "Valid Bearer token must be provided."
    return token
\****************(scope="function", autouse=True)
def precondition_api_reachable():
    """
    Precondition: API is reachable.
    """
    health_url = BASE_URL + "/health"  # Adjust if a health endpoint exists
    try:
        resp = requests.get(health_url, timeout=5)
        assert resp.status_code < 500, f"API not healthy: {resp.status_code}"
    except Exception as e:
        pytest.skip(f"API unreachable: {e}")
\************************\********************\**********************\*************.owasp_asvs(["V5", "V10"])
def test_create_agent_without_slug_returns_422(auth_token):
    """
    TC-POST-1c2d3e4f-001
    Validate that creating an agent without slug returns 422 with validation error.
    Compliance: ISO/IEC/IEEE 29148, RFC 8259, OWASP ASVS V5, V10
    """
    url = BASE_URL + API_ENDPOINT
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    # Compose request body omitting 'slug' (required field)
    payload = {
        "display_name": "Agent Two",  # Example value, can be parameterized
        "category": "testing"          # Example value, must be valid enum
    }
    response = requests.post(url, json=payload, headers=headers)

    # Validate status code
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    # Validate response schema per RFC 8259 (JSON) and OpenAPI error contract
    try:
        resp_json = response.json()
    except Exception as e:
        pytest.fail(f"Response is not valid JSON: {e}")

    assert "detail" in resp_json, "'detail' key missing in error response"
    assert isinstance(resp_json["detail"], list), "'detail' should be a list"

    # Check for missing slug error in detail
    slug_error = next((err for err in resp_json["detail"]
                      if err.get("loc") == ["body", "slug"] and
                         err.get("msg") == "field required" and
                         err.get("type") == "value_error.missing"), None)
    assert slug_error is not None, (
        "Expected validation error for missing 'slug' not found in response detail."
    )

    # Traceability: ISO/IEC/IEEE 29148 (requirements traceability),
    # RFC 8259 (JSON structure), OWASP ASVS V5/V10 (input validation, error handling)

# No teardown required as no data is persisted in negative test.