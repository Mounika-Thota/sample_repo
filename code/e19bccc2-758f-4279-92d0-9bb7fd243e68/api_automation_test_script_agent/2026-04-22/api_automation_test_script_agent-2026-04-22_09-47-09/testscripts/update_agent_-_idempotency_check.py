import os
import requests
import pytest

# Constants for standards compliance
# - Ensure JSON strictly follows RFC 8259 compliant responses
# - Authorization header enforced (OWASP ASVS V10)
# - Test case traceable by id: TC-PUT-55cdd53a-011 (ISO/IEC/IEEE 29148)

# Fixtures for dependency injection
@pytest.fixture(scope='module')
def base_url():
    # Base API URL can be set via environment or config
    return os.environ.get('API_BASE_URL', 'https://api.example.com')

@pytest.fixture(scope='module')
def bearer_token():
    # Token should be fetched securely or set in environment
    token = os.environ.get('API_BEARER_TOKEN')
    if not token:
        pytest.skip('Bearer token not available')
    return token

@pytest.fixture(scope='module')
def agent_id():
    # Agent must exist (precondition)
    agent = os.environ.get('TEST_AGENT_ID')
    if not agent:
        pytest.skip('Agent ID not provided')
    return agent

@pytest.fixture(scope='module')
def put_body():
    # RFC 8259-compliant JSON body (example value)
    return {
        "slug": "idempotent-check"
    }

@pytest.fixture
def cleanup_agent(base_url, bearer_token, agent_id):
    # Cleanup/Teardown step (if mutation required in a real world scenario)
    yield
    # Optionally reset or re-fetch agent to baseline if needed.

@pytest.mark.functional
@pytest.mark.regression
@pytest.mark.owasp_asvs(['V10'])
def test_idempotent_put_agent(base_url, bearer_token, agent_id, put_body, cleanup_agent):
    """
    TC-PUT-55cdd53a-011: Validate making the same update twice does not result in an error, confirming idempotent PUT.
    Standards: RFC 8259 (JSON), OWASP ASVS V10 (Authorization), ISO/IEC/IEEE 29148 (test requirement traceability)
    """
    endpoint = f"{base_url}/api/agents/{agent_id}"
    headers = {
        'Authorization': f'Bearer {bearer_token}',
        'Content-Type': 'application/json'
    }

    # Step 1: Send PUT request
    response1 = requests.put(endpoint, json=put_body, headers=headers)
    assert response1.status_code == 200, f"First PUT failed: {response1.status_code} {response1.text}"
    try:
        data1 = response1.json()
    except Exception as ex:
        pytest.fail(f"First response not valid RFC 8259 JSON: {ex}")

    # Step 2: Repeat same request
    response2 = requests.put(endpoint, json=put_body, headers=headers)
    assert response2.status_code == 200, f"Second PUT (idempotency check) failed: {response2.status_code} {response2.text}"
    try:
        data2 = response2.json()
    except Exception as ex:
        pytest.fail(f"Second response not valid RFC 8259 JSON: {ex}")

    # Validate state consistency (ISO/IEC/IEEE 29148 verification; compare key state fields)
    # Here we expect both responses to at least be semantically equivalent regarding the update
    # For idempotency, system state must not diverge; if known state field (like 'slug'), compare:
    if 'slug' in data1 and 'slug' in data2:
        assert data1['slug'] == put_body["slug"], 'First PUT slug mismatch'
        assert data2['slug'] == put_body["slug"], 'Second PUT slug mismatch'
    # Optionally, compare more fields or GET state if API supports it
    assert data1 == data2, 'System state changed after repeated identical PUT (not idempotent)'

    # End of test - test case fully traceable to source (OWASP ASVS, ISO)
