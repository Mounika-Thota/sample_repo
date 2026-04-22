import pytest
import requests

BASE_URL = "https://api.example.com"  # Replace with the actual host if needed

@pytest.fixture(scope="module")
def api_url():
    """Fixture providing the base API endpoint adhering to RFC 8259."""
    return f"{BASE_URL}/api/agents/"

@pytest.mark.security
@pytest.mark.sanity
@pytest.mark.regression
@pytest.mark.parametrize("invalid_token", [
    "invalidtoken"
])
def test_agents_get_invalid_token(api_url, invalid_token):
    """
    OWASP ASVS: V2, V10
    ISO/IEC/IEEE 29148 Trace: Requirement TC-GET-2e798b8e-05
    Validates that GET /api/agents/ returns 401/403 Unauthorized for invalid Bearer token, and error message aligns to RFC 8259.
    """
    headers = {
        "Authorization": f"Bearer {invalid_token}",
        "Content-Type": "application/json"
    }

    response = requests.get(api_url, headers=headers)

    # Assert expected status code
    assert response.status_code in [401, 403], (
        f"Expected status code 401 or 403, got {response.status_code}."
    )

    # Assert response conforms to RFC 8259, i.e., valid JSON body
    try:
        json_body = response.json()
    except ValueError:
        pytest.fail("Response body is not valid JSON as per RFC 8259.")

    # Assert error message is present in response
    error_fields = ["error", "message", "detail"]
    assert any(field in json_body for field in error_fields), (
        "Expected authentication error message not found in response body."
    )

    # Assert error message content
    error_msg = next((json_body[field] for field in error_fields if field in json_body), "")
    expected_keywords = ["unauthorized", "authentication", "token", "invalid"]
    assert any(kw in error_msg.lower() for kw in expected_keywords), (
        f"Error message does not indicate authentication failure: '{error_msg}'"
    )

    # Standards compliance traceability
    # - RFC 8259: JSON response format
    # - OWASP ASVS V2,V10: Authentication error handling
    # - ISO/IEC/IEEE 29148: Requirement mapping to test case and coverage

@pytest.mark.cleanup
def test_teardown():
    """
    Placeholder for teardown logic; for stateless endpoints, nothing required.
    """
    pass
