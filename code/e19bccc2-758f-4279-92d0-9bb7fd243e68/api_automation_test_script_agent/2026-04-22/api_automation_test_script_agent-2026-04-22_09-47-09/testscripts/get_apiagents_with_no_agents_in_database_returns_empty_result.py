import pytest
import requests
import os

BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:8000')
BEARER_TOKEN = os.environ.get('API_BEARER_TOKEN', '')

@pytest.fixture(scope='function', autouse=True)
def ensure_empty_agents_db():
    """
    Ensure the agent database is empty before the test (ISO/IEC/IEEE 29148 - test setup standards).
    This requires helper API/backdoor - assumed as DELETE /api/agents/
    """
    # Purge agents if such endpoint exists for test environments
    purge_url = f"{BASE_URL}/api/agents/"
    headers = {
        'Authorization': f'Bearer {BEARER_TOKEN}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    # Ignore errors if not present, for idempotency
    requests.delete(purge_url, headers=headers)
    yield
    # (Optional) post-test cleanup could go here if needed

@pytest.mark.sanity
def test_get_agents_empty_db():
    """
    TC-GET-2e798b8e-08
    Validate that an empty agent database results in an empty array/list response.
    OWASP ASVS V10: Ensure no sensitive data is exposed when data is empty.
    RFC 8259: Ensure JSON syntax compliance in responses.
    ISO/IEC/IEEE 29148: Traceable preconditions, test actions, expected outcomes.
    """
    endpoint = f"{BASE_URL}/api/agents/"
    headers = {
        'Authorization': f'Bearer {BEARER_TOKEN}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.get(endpoint, headers=headers)

    # Assert status code
    assert response.status_code == 200, f"Expected HTTP 200 (OK), got {response.status_code}"

    # RFC 8259: Ensure valid JSON
    try:
        body = response.json()
    except Exception as e:
        pytest.fail(f"Response is not valid JSON as per RFC 8259: {e}")

    # Assert response is an array/list
    assert isinstance(body, list), f"Expected response to be a JSON array/list. Got {type(body)}. Body: {body}"

    # Assert response is empty
    assert len(body) == 0, f"Expected empty array/list; got: {body}"
