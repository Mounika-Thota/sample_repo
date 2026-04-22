import pytest
import requests

# Constants (replace with appropriate values, or parametrize as needed)
API_BASE_URL = "https://api.example.com"  # Should be externally configured
AGENT_ENDPOINT = "/api/agents/{agent_id}"  # from automation_metadata
BEARER_TOKEN = None  # Must be provided by higher-level fixtures or env

def get_auth_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

@pytest.fixture(scope="module")
def agent_setup_and_token():
    """
    Fixture to ensure API is reachable, the token is valid, and create a valid agent for test.
    Teardown: delete agent if exists at the end.
    """
    # --- Setup section ---
    # 1. Ensure environment variables/configs provide base URL and token (for traceability to ISO/IEC/IEEE 29148 reqs)
    import os
    token = os.environ.get("API_BEARER_TOKEN")
    assert token, "Valid Bearer token must be provided via API_BEARER_TOKEN env variable."
    # 2. Create a new agent to get its ID (ensure precondition 'agent exists')
    create_url = f"{API_BASE_URL}/api/agents"
    agent_payload = {"name": "IdempotencyTestAgent"}  # Extend as needed
    headers = get_auth_headers(token)
    resp = requests.post(create_url, headers=headers, json=agent_payload)
    assert resp.status_code == 201, f"Expected 201 on agent creation, got {resp.status_code}"
    agent_id = resp.json().get("id")
    assert agent_id, "Agent creation response must include 'id' per RFC 8259 (JSON) and API contract."

    yield agent_id, token

    # --- Teardown section ---
    # Cleanup: Attempt to delete agent if exists (idempotent cleanup, OWASP ASVS safe cleanup)
    delete_url = f"{API_BASE_URL}{AGENT_ENDPOINT.format(agent_id=agent_id)}"
    requests.delete(delete_url, headers=headers)

def is_idempotent_status(code):
    # Accept 200 (OK) or 404 (Not Found) per API idempotency policy
    return code in [200, 404]

def test_agent_delete_idempotency(agent_setup_and_token):
    """
    TC-DELETE-f2e6c865-005
    Ensure the endpoint handles repeated deletions gracefully to confirm idempotency.
    Standards: RFC 8259 (JSON), OWASP ASVS (V2, V10), ISO/IEC/IEEE 29148 (Requirements Traceability)
    """
    agent_id, token = agent_setup_and_token
    headers = get_auth_headers(token)
    delete_url = f"{API_BASE_URL}{AGENT_ENDPOINT.format(agent_id=agent_id)}"

    # Step 1: Send DELETE request (first time): agent should be deleted (status 200)
    resp1 = requests.delete(delete_url, headers=headers)
    assert resp1.status_code == 200, f"First DELETE: Expected 200 (deleted), got {resp1.status_code}."
    # (Optional) Validate schema compliance with expected JSON if any per RFC 8259 (not defined here)

    # Step 2: Send DELETE request again (second time): status should be 200 or 404 or appropriate idempotent result
    resp2 = requests.delete(delete_url, headers=headers)
    assert is_idempotent_status(resp2.status_code), \
        f"Second DELETE: Expected 200 or 404 for idempotent delete, got {resp2.status_code}."

    # If API returns a body, ensure response is valid JSON per RFC 8259
    if resp2.content:
        try:
            resp2.json()
        except ValueError:
            pytest.fail("Second DELETE: Response body must be valid JSON as per RFC 8259.")
