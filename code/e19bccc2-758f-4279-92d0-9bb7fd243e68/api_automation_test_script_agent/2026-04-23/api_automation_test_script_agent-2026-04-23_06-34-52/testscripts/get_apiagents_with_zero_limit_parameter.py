import os
import requests
import pytest

# Constants - API configuration (Should come from environment or fixtures for compliance)
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.example.com")
API_ENDPOINT = "/api/agents/"
\****************(scope="session")
def bearer_token():
    """
    Fixture for fetching bearer token from environment or fixture manager.
    Maintains compliance with OWASP ASVS (V5 - authentication, session management).
    """
    token = os.getenv("API_BEARER_TOKEN")
    assert token is not None and token != "<REPLACE_WITH_TOKEN>", \
        "Bearer token must be set in environment for traceability (ISO/IEC/IEEE 29148)."
    return token
\****************(scope="module")
def api_headers(bearer_token):
    """
    Returns compliant headers for API requests (RFC 8259/OWASP ASVS).
    """
    return {
        'Authorization': f'Bearer {bearer_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

def validate_agents_empty_response(resp_json):
    """
    Validates that response contains zero agents (traceable to reqs TC-GET-2f1c1c7e-006, ISO/IEC/IEEE 29148, RFC 8259).
    Accepts any structure as per actual API schema. Adjust checks accordingly for the attribute name.
    """
    if isinstance(resp_json, list):
        # OpenAPI: Returns a list
        assert len(resp_json) == 0, "Expected empty list when 'limit=0'."
    elif isinstance(resp_json, dict):
        # If wrapped in object (e.g., {"agents": []})
        if 'agents' in resp_json:
            assert isinstance(resp_json['agents'], list), "'agents' property must be a list as per JSON contract."
            assert len(resp_json['agents']) == 0, "'agents' list must be empty when limit=0."
        else:
            # Accept server's documented empty state
            assert not resp_json, "Dictionary response should be empty for limit=0 (ISO/IEC/IEEE 29148: explicitness)."
    else:
        # Schema nonconformance
        pytest.fail("Response JSON structure not as per API specification (RFC 8259 compliance).")
\**********************\************************\*************.owasp_v5\*************.iso_isoiec_ieee_29148\*************.rfc8259
def test_get_agents_limit_zero(api_headers):
    """
    TC-GET-2f1c1c7e-006: Validate GET /api/agents/?limit=0 returns an empty list or appropriate response.\n
    Standards alignment:
      - RFC 8259 (JSON content)
      - OWASP ASVS V5 (API Auth, response validation)
      - ISO/IEC/IEEE 29148 (clear, verifiable requirements, traceability)
    """
    url = f"{API_BASE_URL}{API_ENDPOINT}"
    params = {'limit': 0}

    # Step: Send GET request
    response = requests.get(url, headers=api_headers, params=params, timeout=10)

    # Expected Result 1: Status 200
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    assert response.headers.get('Content-Type', '').startswith('application/json'), \
        "Response must be JSON as per RFC 8259."
    try:
        resp_json = response.json()
    except Exception as e:
        pytest.fail(f"Response is not valid JSON: {e}")
    
    # Expected Result 2: Response body contains zero agents
    validate_agents_empty_response(resp_json)
