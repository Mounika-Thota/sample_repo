import pytest
import requests
import string
import random

API_BASE_URL = 'https://api.example.com'  # Replace with actual API URL
ENDPOINT = '/api/agents/'
TOKEN = '<REPLACE_WITH_TOKEN>'  # This should be set via secure config or env variable

@pytest.fixture(scope='module')
def auth_header():
    # Ensures traceability and token management as per OWASP ASVS Section V5 (Authentication)
    assert TOKEN != '<REPLACE_WITH_TOKEN>', "Bearer token must be securely provided."
    return {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }

def random_string(length):
    # Utility to generate RFC 8259 valid JSON string value
    chars = string.ascii_letters + string.digits + "-_"
    return ''.join(random.choices(chars, k=length))

@pytest.fixture
def agent_payload():
    # Ensures field lengths at API boundary per ISO/IEC/IEEE 29148 (Requirement 3.9.2, specifying boundaries)
    slug = random_string(255)
    display_name = random_string(255)
    category = 'testing'  # Valid enum value as per OpenAPI spec
    return {
        'slug': slug,
        'display_name': display_name,
        'category': category
    }

created_agents = []  # To track cleanup

@pytest.fixture(autouse=True)
def teardown_created_agents():
    yield
    # Cleanup step as per good practice (ISO/IEC/IEEE 29148 6.4.3.3 Verification)
    for agent in created_agents:
        try:
            requests.delete(
                API_BASE_URL + ENDPOINT + str(agent['id']),
                headers={'Authorization': f'Bearer {TOKEN}'}
            )
        except Exception:
            pass

def test_post_agents_boundary_lengths(auth_header, agent_payload):
    """
    TC-POST-7dead6b2-004: Validate POST /api/agents/ accepts and handles boundary field lengths
    for 'slug' and 'display_name'. Standards: RFC8259 (JSON), OWASP ASVS V5/V10, ISO/IEC/IEEE 29148
    """
    response = requests.post(
        API_BASE_URL + ENDPOINT,
        json=agent_payload,
        headers=auth_header,
        timeout=10
    )
    # RFC 8259: Valid JSON structure required in body
    assert response.headers.get('Content-Type', '').startswith('application/json'),
        'Response must have Content-Type application/json (RFC 8259)'
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    resp_json = response.json()
    # ISO/IEC/IEEE 29148 compliance: output reflects input boundary
    for field in ['slug', 'display_name']:
        assert resp_json.get(field) == agent_payload[field], \
            f"Response {field} should reflect boundary input.\nExpected: {agent_payload[field]}, Actual: {resp_json.get(field)}"
    # (Traceable to fields)
    assert resp_json.get('category') == 'testing', "Category should be 'testing' per valid enum."
    # Store created agent id for teardown
    if 'id' in resp_json:
        created_agents.append({'id': resp_json['id']})