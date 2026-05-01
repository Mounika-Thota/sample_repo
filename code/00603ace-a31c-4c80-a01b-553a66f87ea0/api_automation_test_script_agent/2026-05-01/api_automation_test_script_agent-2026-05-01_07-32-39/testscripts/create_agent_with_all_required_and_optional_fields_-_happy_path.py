import pytest
import requests
import os

BASE_URL = os.getenv('API_BASE_URL', 'https://api.example.com')  # ISO/IEC/IEEE 29148: Configurable endpoint
TOKEN = os.getenv('BEARER_TOKEN')  # ISO/IEC/IEEE 29148: Token from secure env
\****************(scope='module')
def valid_headers():
    """RFC 8259: Use valid authorization and content headers; OWASP ASVS: ensure secure transport."""
    assert TOKEN is not None, "Bearer token must be set in environment variables."
    return {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }
\****************(scope='module')
def agent_payload():
    """Compliant payload including required and optional fields."""
    # Slug and display_name: ISO/IEC/IEEE 29148 traceability for field definitions
    return {
        'slug': 'pytest-agent',
        'display_name': 'Pytest Agent',
        'category': 'testing',
        'description': 'An agent for pytest automation',
        'parent_id': 'parent12345'
    }

def test_create_new_agent(valid_headers, agent_payload):
    """
    Testcase ID: TC-POST-9a0eda3c-001
    Description: Validate creation of a new agent with all required/optional fields.
    Compliance: ISO/IEC/IEEE 29148 §5.7.3, RFC 8259 (JSON), OWASP ASVS V2, V5, V10
    """
    # Step 1: API reachability check (traceability: ISO/IEC/IEEE 29148 §7.2.3)
    health_resp = requests.get(f"{BASE_URL}/health")
    assert health_resp.status_code in [200, 201], "API is not reachable."

    # Step 2: Send POST request per RFC 8259
    response = requests.post(f"{BASE_URL}/api/agents/", json=agent_payload, headers=valid_headers)

    # Expected Result 1: Status code 200 (OWASP ASVS V2: appropriate status codes)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    # Expected Result 2: Response body contains details of new agent (ISO/IEC/IEEE 29148 verifiability)
    resp_data = response.json()
    # Traceability: Check for required response fields
    assert 'slug' in resp_data and resp_data['slug'] == agent_payload['slug'], 'Slug mismatch or missing.'
    assert 'display_name' in resp_data and resp_data['display_name'] == agent_payload['display_name'], 'Display name mismatch or missing.'
    assert 'category' in resp_data and resp_data['category'] == agent_payload['category'], 'Category mismatch or missing.'
    assert 'description' in resp_data and resp_data['description'] == agent_payload['description'], 'Description mismatch or missing.'
    assert 'parent_id' in resp_data and resp_data['parent_id'] == agent_payload['parent_id'], 'Parent id mismatch or missing.'
    # OWASP ASVS V5: No sensitive info in response
    assert 'token' not in resp_data, 'Response should not expose sensitive data.'

    # Teardown: (optional) cleanup if agent created successfully
    agent_id = resp_data.get('id')
    if agent_id:
        cleanup_resp = requests.delete(f"{BASE_URL}/api/agents/{agent_id}", headers=valid_headers)
        assert cleanup_resp.status_code in [200, 204], f"Cleanup failed with status {cleanup_resp.status_code}"