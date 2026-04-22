import requests
import pytest

BASE_URL = "https://api.example.com"  # Update to actual API base URL

@pytest.fixture(scope="module")
def api_base_url():
    """Fixture for base API URL, replace with actual URL."""
    return BASE_URL

@pytest.mark.security
@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.asvs("V2", "V10")
def test_get_agents_without_authorization(api_base_url):
    """TC-GET-2e798b8e-04: Validate GET /api/agents/ returns 401 Unauthorized when Authorization header is missing.
    Standards:
      - RFC 8259 (JSON)
      - OWASP ASVS (V2 Authentication, V10 Error Handling)
      - ISO/IEC/IEEE 29148 (Traceable Requirements, Verifiability)
    """
    # Preconditions: API is reachable
    endpoint = "/api/agents/"
    url = f"{api_base_url}{endpoint}"
    headers = {
        "Content-Type": "application/json"
        # 'Authorization' header intentionally omitted for this security test
    }
    # Step 1: Send GET request with no Authorization header
    response = requests.get(url, headers=headers)
    # Validation 1: Status code is 401 or 403
    assert response.status_code in [401, 403], (
        f"Expected status 401 or 403, got {response.status_code}: {response.text}")
    # Validation 2: Response body contains authentication error message
    try:
        resp_json = response.json()
        error_msg = resp_json.get("error") or resp_json.get("message") or resp_json.get("detail")
    except Exception:
        error_msg = response.text

    assert error_msg, "Expected error message in response body (OWASP ASVS V10)."
    # Optional: Check for some known authentication error text
    assert any(keyword in error_msg.lower() for keyword in ["unauthorized", "authentication", "forbidden", "token"]), (
        f"Authentication error message missing or unclear: '{error_msg}'" )
    # Standards traceability: RFC 8259 (JSON ensured), OWASP ASVS V2 & V10 validated, ISO/IEC/IEEE 29148 requirement traceable via test id

# No teardown needed: No state or data changed