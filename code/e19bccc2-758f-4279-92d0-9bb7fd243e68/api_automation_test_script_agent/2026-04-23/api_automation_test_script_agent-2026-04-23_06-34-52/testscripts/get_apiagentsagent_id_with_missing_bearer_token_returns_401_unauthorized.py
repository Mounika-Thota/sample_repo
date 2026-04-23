import pytest
import requests

BASE_URL = "https://api.example.com"  # Replace this with the actual API base URL if available
\****************(scope="module")
def agent_id():
    """
    Setup: Ensure that an agent exists and return a valid agent_id.
    This fixture should be updated to retrieve/validate an actual agent ID in live/test environment.
    """
    # Compliance with ISO/IEC/IEEE 29148: requirements traceability
    # In an actual deployment, retrieve via authenticated API call or DB lookup.
    # Here, agent ID must be provided externally for compliance and reproducibility.
    return "REPLACE_WITH_AGENT_ID"
\**********************\************************\******************("V2")  # OWASP ASVS V2: Authentication\******************("V10") # OWASP ASVS V10: Error Handling & Logging\*************.risk_level("high")
def test_get_agent_without_auth_returns_401(agent_id):
    """
    TC-GET-2e2e0c6c-002: Validate that a GET request to /api/agents/{agent_id}
    without an Authorization header returns HTTP 401 Unauthorized.
    Standards: RFC 8259 (JSON syntax), OWASP ASVS (V2, V10), ISO/IEC/IEEE 29148.
    """
    endpoint = f"{BASE_URL}/api/agents/{agent_id}"

    # Precondition: API is reachable
    # Traceability: API liveness check (ISO/IEC/IEEE 29148)
    try:
        health_resp = requests.get(f"{BASE_URL}/health")
        assert health_resp.status_code == 200, "API health endpoint not reachable"
    except Exception as e:
        pytest.skip(f"API not reachable: {e}")

    # Step: Send GET request WITHOUT Authorization header
    headers = {}  # No Authorization header as per test case
    resp = requests.get(endpoint, headers=headers)

    # RFC 8259: payload must be valid JSON if content-type is application/json
    content_type = resp.headers.get('Content-Type', '').lower()
    is_json = 'application/json' in content_type

    # Expected: Status 401
    assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"

    # Expected: Error message indicating missing or invalid authentication
    if is_json:
        try:
            body = resp.json()
        except Exception as e:
            pytest.fail(f"Response claims JSON but isn't valid: {e}")
        assert any(key in body for key in ["error", "message", "detail"]), \
            "Error message field missing per OWASP ASVS V10"
        # OWASP ASVS: Don't leak implementation, ensure generic message
        expected_phrases = ["missing authentication", "invalid authentication", "unauthorized", "not authorized"]
        actual_msg = str(body.get("error", "")) + str(body.get("message", "")) + str(body.get("detail", ""))
        assert any(phrase in actual_msg.lower() for phrase in expected_phrases), \
            f"Error message does not indicate missing/invalid authentication: {actual_msg}"
    else:
        # If not JSON, check raw text for expected phrases
        actual_msg = resp.text.lower()
        expected_phrases = ["missing authentication", "invalid authentication", "unauthorized", "not authorized"]
        assert any(phrase in actual_msg for phrase in expected_phrases), \
            f"Error message does not indicate missing/invalid authentication in raw payload: {actual_msg}"

    # Compliance traceability links:
    # - RFC 8259: Valid JSON syntax checks
    # - OWASP ASVS V2: Authentication control enforced
    # - OWASP ASVS V10: Proper error handling without sensitive info leakage
    # - ISO/IEC/IEEE 29148: Each requirement verifiable via assertion

# To execute: pytest -v test_security_get_agent_noauth.py
