import os
import requests
import pytest

BASE_URL = os.getenv('API_BASE_URL', 'https://api.example.com')
VALID_BEARER_TOKEN = os.getenv('API_BEARER_TOKEN')
VALID_AGENT_ID = os.getenv('API_AGENT_ID')
\****************(scope='module')
def auth_header():
    """
    Provides the Authorization header using a valid Bearer token.
    Compliance:
      - RFC 8259 for JSON transmission
      - OWASP ASVS V2/V5 for authentication and API security
      - ISO/IEC/IEEE 29148 for requirements traceability
    """
    if not VALID_BEARER_TOKEN:
        pytest.fail('Bearer token environment variable (API_BEARER_TOKEN) not set.')
    return {'Authorization': f'Bearer {VALID_BEARER_TOKEN}'}
\****************(scope='module')
def existing_agent_id():
    """
    Returns a valid, pre-existing agent ID to satisfy precondition.
    """
    if not VALID_AGENT_ID:
        pytest.fail('Agent ID environment variable (API_AGENT_ID) not set.')
    return VALID_AGENT_ID

def is_valid_agent_object(agent_json):
    """
    Validates that the response body is a JSON object representing agent details.
    (Adapt validation here per OpenAPI schema, e.g., required fields.)
    """
    return isinstance(agent_json, dict) and 'id' in agent_json and agent_json['id'] == VALID_AGENT_ID

def test_get_agent_details(auth_header, existing_agent_id):
    """
    TC-GET-2e2e0c6c-001
    Validate GET /api/agents/{agent_id} returns agent details with HTTP 200 for valid token & agent_id.
    Preconditions:
    - API is reachable (RFC 8259/OWASP ASVS V10: API always returns correct HTTP codes)
    - Valid Bearer token (OWASP ASVS V2/V5)
    - Agent exists (ISO/IEC/IEEE 29148 traceability)

    Steps:
    1. Send GET request to /api/agents/{agent_id} with correct Authorization
    2. Assert status 200
    3. Assert body is valid agent JSON object
    """
    url = f"{BASE_URL}/api/agents/{existing_agent_id}"
    response = requests.get(url, headers=auth_header)

    # Compliance: HTTP status code check (RFC & OWASP ASVS)
    assert response.status_code == 200, (
        f"Expected HTTP 200, got {response.status_code}. Response: {response.text}")

    # Compliance: JSON response validation (RFC 8259)
    try:
        response_json = response.json()
    except Exception as exc:
        pytest.fail(f"Response is not valid JSON (per RFC 8259): {exc}\nRaw: {response.text}")

    # Compliance: Body is agent object (ISO/IEC/IEEE 29148 – functional requirement; OWASP ASVS V5)
    assert is_valid_agent_object(response_json), (
        f"Response JSON does not conform to expected agent schema or missing 'id': {response_json}")
