import pytest
import requests

# Standards compliance notes:
# - RFC 8259 (JSON): All request/response bodies are JSON compliant.
# - OWASP ASVS (V2, V10): Test case verifies authorization enforcement, prevents access with invalid credentials.
# - ISO/IEC/IEEE 29148: Requirements are uniquely traceable to test case 'TC-POST-7f2b9c6b-011'.

BASE_URL = 'http://localhost'  # Replace with API's actual base URL if needed.
ENDPOINT = '/api/agents/'
\****************(scope='module')
def api_url():
    """
    Fixture to build the full API endpoint URL.
    """
    return BASE_URL.rstrip('/') + ENDPOINT
\****************(scope='module')
def payload():
    """
    Provides an example valid request payload, as per OpenAPI spec and test input.
    """
    return {
        'slug': 'agent-011',
        'display_name': 'Agent Eleven',
        'category': 'testing'
    }
\**********************\************************\*************.owasp_asvs(['V2', 'V10'])
def test_post_agents_invalid_authorization(api_url, payload):
    """
    TC-POST-7f2b9c6b-011: Validate error response when Authorization header contains invalid token.
    ASVS V2: Authentication, V10: Error Handling.
    """
    headers = {
        'Authorization': 'Bearer <INVALID_TOKEN>',  # Explicitly invalid token as per test case
        'Content-Type': 'application/json',
    }

    # Step: Send POST request to /api/agents/ with invalid Authorization token
    resp = requests.post(api_url, json=payload, headers=headers)

    # Validate Status 401
    assert resp.status_code == 401, (
        f"Expected 401 Unauthorized, got {resp.status_code}. Response: {resp.text}"
    )

    # Validate that the response body contains an error indicating unauthorized access
    try:
        resp_json = resp.json()
    except ValueError:
        pytest.fail(f"Response is not valid JSON: {resp.text}")
    error_fields = ('error', 'message', 'detail', 'code', 'errors')
    error_present = any(k in resp_json and ('unauth' in str(resp_json[k]).lower() or 'invalid token' in str(resp_json[k]).lower())
                       for k in error_fields)
    
    assert error_present, (
        f"Expected error message about unauthorized access or invalid token, got: {resp_json}"
    )
\****************(scope='module', autouse=True)
def teardown_invalid_agent(request):
    """
    (No teardown necessary: no valid agent can be created with invalid token; placeholder for ISO/IEC/IEEE 29148 completeness.)
    """
    yield
    # No resource cleanup required.
