import pytest
import requests

# Constants - Replace with environment config as needed
BASE_URL = "https://api.example.com"  # Update with actual base URL
def get_bearer_token():
    """Retrieve bearer token securely from environment/config."""
    # For compliance: Avoid hardcoded tokens, retrieve securely
    return "<REPLACE_WITH_TOKEN>"
\****************(scope="module")
def api_headers():
    """Setup: Prepare request headers with valid bearer token."""
    return {
        "Authorization": f"Bearer {get_bearer_token()}",
        "Content-Type": "application/json"
    }
\****************(scope="module")
def api_endpoint():
    """Setup: Target endpoint for POST."""
    return f"{BASE_URL}/api/agents/"
\************************\*************.owasp_asvs("V10")  # OWASP ASVS ref for input validation\*************.risk_level("medium")
def test_post_agents_invalid_json(api_headers, api_endpoint):
    """TC-POST-7f2b9c6b-020: Validate error response when request body is not valid JSON (RFC 8259/OWASP ASVS V10)."""
    # Step: Send malformed JSON body
    malformed_json = "{'invalid': 'json'}"  # Single quotes: not valid JSON per RFC 8259
    
    response = requests.post(api_endpoint, data=malformed_json, headers=api_headers)

    # Expected: Status 400
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"  # ISO/IEC/IEEE 29148: verifiable requirement

    # Expected: Response body contains error indicating invalid JSON
    try:
        body = response.json()
        assert any(word in str(body).lower() for word in ["invalid json", "malformed json", "parse error", "syntax error"]), \
            "Response body should indicate invalid JSON syntax (RFC 8259, OWASP ASVS V10)."
    except ValueError:
        # Not JSON (may be text)
        assert any(word in response.text.lower() for word in ["invalid json", "malformed json", "parse error", "syntax error"]), \
            "Response body should indicate invalid JSON syntax (RFC 8259, OWASP ASVS V10)."

    # Traceability Notes:
    # - RFC 8259: Enforces strict JSON syntax. Test uses invalid JSON & expects compliant error.
    # - OWASP ASVS V10: Input validation & error handling for malformed JSON.
    # - ISO/IEC/IEEE 29148: Each assertion aligns with verifiable requirements & expected outcomes.

def teardown_module(module):
    """Teardown: No cleanup required as this is a negative test (does not create resources)."""
    pass
