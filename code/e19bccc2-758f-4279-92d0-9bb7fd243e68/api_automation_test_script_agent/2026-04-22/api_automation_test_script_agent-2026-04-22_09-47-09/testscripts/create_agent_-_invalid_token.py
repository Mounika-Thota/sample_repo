import pytest
import requests

BASE_URL = "https://api.example.com"  # Update to actual API base URL

@pytest.fixture(scope="module")
def api_base_url():
    # Setup: Confirm API is reachable (ISO/IEC/IEEE 29148: precondition traceability)
    health_url = f"{BASE_URL}/health"
    resp = requests.get(health_url)
    assert resp.status_code in [200, 204], f"API not reachable: {health_url} status {resp.status_code}"
    return BASE_URL

@pytest.mark.security
@pytest.mark.sanity
@pytest.mark.asvs('V2', 'V10')
def test_post_agents_with_invalid_or_missing_token(api_base_url):
    """
    TC-POST-7dead6b2-003
    Validate POST /api/agents/ fails with 401 when an invalid or missing Bearer token is used.
    Standards: RFC 8259 (JSON payload/response), OWASP ASVS (V2, V10), ISO/IEC/IEEE 29148 (requirement traceability)
    """
    url = f"{api_base_url}/api/agents/"
    payload = {
        "slug": "agent-slug-unauth",
        "display_name": "Agent Unauthorized",
        "category": "usg"
    }
    headers = {
        "Authorization": "Bearer <INVALID_TOKEN>",  # Invalid token as per testcase
        "Content-Type": "application/json"
    }
    # Step 1: Send POST request with invalid Authorization header (OWASP ASVS V10 authentication control)
    response = requests.post(url, json=payload, headers=headers)
    # RFC 8259: Strict JSON
    assert response.headers.get('Content-Type', '').startswith('application/json'), "Response is not JSON as per RFC 8259"
    # ASVS V2: Authentication error handling
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    resp_json = response.json()
    # ISO/IEC/IEEE 29148: Requirement traceability on error messages
    assert 'error' in resp_json or 'message' in resp_json, "Error message not found in response body"
    auth_msgs = ["auth", "token", "unauthorized", "authentication"]
    msg = resp_json.get('error', '') or resp_json.get('message', '')
    assert any(keyword in msg.lower() for keyword in auth_msgs), f"Response error message not related to authentication: {msg}"

    # Step 2: Send POST request with missing Authorization header
    headers_missing = {"Content-Type": "application/json"}
    response_missing = requests.post(url, json=payload, headers=headers_missing)
    assert response_missing.headers.get('Content-Type', '').startswith('application/json'), "Response is not JSON as per RFC 8259 (missing token)"
    assert response_missing.status_code == 401, f"Expected 401 with missing token, got {response_missing.status_code}"
    resp_missing_json = response_missing.json()
    assert 'error' in resp_missing_json or 'message' in resp_missing_json, "Error message not found in response body (missing token)"
    msg_missing = resp_missing_json.get('error', '') or resp_missing_json.get('message', '')
    assert any(keyword in msg_missing.lower() for keyword in auth_msgs), f"Response error message not related to authentication (missing token): {msg_missing}"
