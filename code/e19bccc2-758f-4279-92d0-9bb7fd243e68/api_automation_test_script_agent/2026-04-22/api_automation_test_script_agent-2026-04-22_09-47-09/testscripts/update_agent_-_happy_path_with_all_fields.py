import pytest
import requests
import os

# Constants (should be replaced by proper secure secret management or ENV variables)
BASE_URL = os.getenv('API_BASE_URL', 'https://api.example.com')
TOKEN = os.getenv('API_BEARER_TOKEN')
AGENT_ID = os.getenv('API_AGENT_ID')

@pytest.fixture(scope='module')
def auth_header():
    assert TOKEN is not None, "Bearer token must be set in environment variable API_BEARER_TOKEN (ASVS V2, V5)"
    return {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}

@pytest.fixture(scope='module')
def agent_id():
    assert AGENT_ID is not None, "Agent ID must be specified in environment variable API_AGENT_ID"
    return AGENT_ID

def build_full_agent_body():
    # Example body with all fields set to non-null values, as per OpenAPI metadata and ISO/IEC/IEEE 29148 traceability
    return {
        'slug': 'new-agent-slug',
        'display_name': 'Agent Display Name',
        'category': 'testing',
        'description': 'Agent description updated',
        'parent_id': 'parent123',
    }

@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.sanity
@pytest.mark.functional
@pytest.mark.owasp_asvs_refs(['V2', 'V5', 'V10'])
def test_update_agent_all_fields(auth_header, agent_id):
    """
    Validate updating agent with all possible fields set results in 200 success.
    Compliance: RFC 8259 (JSON structure), OWASP ASVS (V2, V5, V10), ISO/IEC/IEEE 29148 traceability
    """
    url = f"{BASE_URL}/api/agents/{agent_id}"
    body = build_full_agent_body()

    # Step: Send PUT request with all fields non-null
    resp = requests.put(url, headers=auth_header, json=body)

    # Assert 1: Status 200 (OWASP ASVS V5, traceable)
    assert resp.status_code == 200, f"Expected status 200, got {resp.status_code}: {resp.text}"

    # Assert 2: Content-Type valid and response body is valid JSON (RFC 8259, ASVS V10)
    assert 'application/json' in resp.headers.get('Content-Type', ''), \
        f"Expected application/json content type. Got: {resp.headers.get('Content-Type')}"
    try:
        result_json = resp.json()
    except ValueError as e:
        pytest.fail(f"Response body is not valid JSON: {e}\nRaw text: {resp.text}")

    # Further schema checks are omitted due to unspecified response schema, but add basic checks for non-emptiness
    assert isinstance(result_json, dict), "Response body must be a JSON object (RFC 8259)"
    assert result_json, "Response JSON should not be empty"

# Optionally, add data cleanup/teardown if agent state needs reverting. Ensure traceability with all requirements per ISO/IEC/IEEE 29148.
