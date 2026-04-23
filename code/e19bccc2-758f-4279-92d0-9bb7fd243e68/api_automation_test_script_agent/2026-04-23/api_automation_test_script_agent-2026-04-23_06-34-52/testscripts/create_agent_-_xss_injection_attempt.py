import os
import pytest
import requests
from urllib.parse import urljoin

def get_bearer_token():
    """
    Fetch bearer token from environment or secrets manager.
    Replace logic as needed for CI/CD integration.
    """
    token = os.environ.get("API_BEARER_TOKEN")
    if not token:
        raise EnvironmentError("Bearer token not found. Set API_BEARER_TOKEN environment variable.")
    return token
\****************(scope="module")
def api_base_url():
    """Provide the base API URL (ensure this follows environment configurations for repeatable testing)."""
    base_url = os.environ.get("API_BASE_URL", "http://localhost:8000")
    return base_url
\****************(scope="module")
def auth_header():
    token = get_bearer_token()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def is_xss_reflected(response_json, xss_payload):
    """Checks if the payload is reflected in any string field."""
    def walk(obj):
        if isinstance(obj, dict):
            for v in obj.values():
                if walk(v):
                    return True
        elif isinstance(obj, list):
            for v in obj:
                if walk(v):
                    return True
        elif isinstance(obj, str):
            if xss_payload in obj:
                return True
        return False
    return walk(response_json)
\**********************\************************\*************.owasp_v5\*************.owasp_v10
def test_input_sanitization_description_field(api_base_url, auth_header):
    """
    TC-POST-7f2b9c6b-015
    Validate input sanitization by sending XSS payload in description field.
    OWASP ASVS: V5, V10 compliance.
    RFC 8259 (JSON).
    ISO/IEC/IEEE 29148 traceable requirement: Input validation, security controls, traceability.
    """
    endpoint = "/api/agents/"
    url = urljoin(api_base_url, endpoint)
    xss_payload = "<script>alert('XSS')</script>"
    test_agent_slug = "agent-xss-pytest"

    payload = {
        "slug": test_agent_slug,
        "display_name": "Agent XSS",
        "category": "testing",
        "description": xss_payload
    }

    # --- Step 1: Send POST request with XSS payload ---
    response = requests.post(url, json=payload, headers=auth_header)
    assert response.status_code in [200, 422], (
        f"Expected status 200 or 422, got {response.status_code}. Response: {response.text}")

    # --- Step 2: Validate response body does not reflect or execute XSS ---
    try:
        response_json = response.json()
    except Exception:
        response_json = None

    if response.status_code == 200:
        # RFC 8259: Response must be well-formed JSON
        assert response_json is not None, "Response must be in JSON format as per RFC 8259."
        # ISO/IEC/IEEE 29148: Response must not reflect input scripts unfiltered (requirement: input validation)
        # OWASP ASVS V5/V10: Test for XSS reflection
        assert not is_xss_reflected(response_json, xss_payload), (
            "Potential XSS reflection detected in response body. Input must be sanitized.")
    elif response.status_code == 422:
        # Unprocessable entity: Input validation works (V5, ISO/IEC/IEEE 29148)
        assert response_json is not None, "422 should return a machine-readable JSON error."
        # Optionally check content of error for traceability/compliance
        assert 'error' in response_json or 'detail' in response_json, (
            "422 response should have 'error' or 'detail' field as per API spec.")
        # Should not reflect the XSS payload in error messages either
        assert not is_xss_reflected(response_json, xss_payload), (
            "XSS payload reflected in error message. API must sanitize input in error responses.")

    # -- Optional: Cleanup if test agent was created --
    if response.status_code == 200 and response_json:
        agent_id = response_json.get('id')
        if agent_id:
            delete_url = urljoin(api_base_url, f"/api/agents/{agent_id}")
            requests.delete(delete_url, headers=auth_header)
