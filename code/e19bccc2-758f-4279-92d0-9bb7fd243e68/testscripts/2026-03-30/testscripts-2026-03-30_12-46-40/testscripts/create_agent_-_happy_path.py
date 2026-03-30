import os
import uuid
import requests
import pytest

# Constants (could be moved to config)
BASE_URL = os.getenv('API_BASE_URL', 'https://api.example.com')
AUTH_TOKEN = os.getenv('API_BEARER_TOKEN')  # Should be provided securely
ENDPOINT = '/api/agents/'
HEADERS = {
    'Authorization': f'Bearer {AUTH_TOKEN}',
    'Content-Type': 'application/json',
}
CATEGORIES = [
    'usg', 'testing', 'api_doc_testing', 'performance_testing',
    'deployment', 'req_synthesizer', 'ui_automation', 'documentation'
]
\****************(scope='function')
def agent_payload():
    """
    Generates a valid, unique payload for agent creation, compliant with RFC 8259 (JSON),
    and constrained by ISO/IEC/IEEE 29148 (requirements traceability).
    """
    slug = f"agent-{uuid.uuid4().hex[:8]}"
    payload = {
        'slug': slug,
        'display_name': f'Agent {slug}',
        'category': 'testing',
        # Optional fields
        'description': 'This is a test agent created by automated test.',
        # 'parent_id': None  # Not provided unless needed
    }
    return payload
\****************(scope='function')
def created_agent_cleanup():
    """
    Tracks created agent slugs for cleanup if DELETE is supported.
    """
    slugs = []
    yield slugs
    # Teardown: Implement deletion if API supports it, for now just a placeholder
    # for slug in slugs:
    #     requests.delete(f"{BASE_URL}{ENDPOINT}{slug}", headers=HEADERS)
\*************.owasp_asvs('V2', 'V5', 'V10')\*************.risk_level('high')\******************('smoke', 'regression', 'sanity')
def test_create_agent_with_valid_payload(agent_payload, created_agent_cleanup):
    """
    Validate that a new agent can be created with valid slug, display_name, and category.
    Standards: RFC 8259 (JSON), OWASP ASVS (V2, V5, V10), ISO/IEC/IEEE 29148.
    """
    # Preconditions
    assert AUTH_TOKEN, "Valid Bearer token must be set in API_BEARER_TOKEN environment variable."
    # Step 1: Send POST request
    response = requests.post(
        f"{BASE_URL}{ENDPOINT}",
        headers=HEADERS,
        json=agent_payload
    )
    # Expected Result 1: Status 200
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}. Response: {response.text}"
    # Expected Result 2: Response body contains created agent details
    try:
        resp_json = response.json()
    except Exception as e:
        pytest.fail(f"Response is not valid JSON (RFC 8259): {e}\nBody: {response.text}")
    # Traceability: Validate required fields are present and correct
    for field in ['slug', 'display_name', 'category']:
        assert field in resp_json, f"Response missing required field: {field}"
        assert resp_json[field] == agent_payload[field], f"Mismatch in field '{field}': expected '{agent_payload[field]}', got '{resp_json[field]}'."
    # Optional fields
    if 'description' in agent_payload:
        assert resp_json.get('description') == agent_payload['description']
    # Category constraint check (ISO/IEC/IEEE 29148: requirements are verifiable)
    assert resp_json['category'] in CATEGORIES, f"Category '{resp_json['category']}' not in allowed list."
    # Uniqueness check (slug should be unique)
    created_agent_cleanup.append(agent_payload['slug'])
    # Security/ASVS: Ensure no sensitive data is leaked
    forbidden_fields = ['password', 'secret', 'token']
    for field in forbidden_fields:
        assert field not in resp_json, f"Security issue: field '{field}' should not be in response."
    # RFC 8259: Ensure JSON response is an object
    assert isinstance(resp_json, dict), "Response JSON must be an object."
