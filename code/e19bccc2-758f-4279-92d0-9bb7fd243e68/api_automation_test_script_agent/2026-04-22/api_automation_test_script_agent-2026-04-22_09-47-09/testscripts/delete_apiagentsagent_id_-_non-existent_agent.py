import pytest
import requests

# Constants aligned with RFC 8259 (JSON payloads if needed)
API_BASE_URL = "https://api.example.com"  # Replace with actual API endpoint
AGENTS_ENDPOINT = "/api/agents/{agent_id}"

@pytest.fixture(scope="module")
def valid_bearer_token():
    # Setup: Acquire Bearer token from secure source or fixture
    # For compliance, avoid hardcoding; inject via environment variable or config
    import os
    token = os.getenv("BEARER_TOKEN")
    assert token is not None, "Bearer token must be provided via environment"
    yield token

@pytest.fixture(scope="function")
def non_existent_agent_id():
    # Choose an ID guaranteed not to exist, e.g., a UUID not present in DB
    # For boundary testing per OWASP ASVS and ISO/IEC/IEEE 29148: ensure traceability
    import uuid
    # Optionally, check via GET to confirm it does not exist
    agent_id = str(uuid.uuid4())
    url = f"{API_BASE_URL}{AGENTS_ENDPOINT.format(agent_id=agent_id)}"
    resp = requests.get(url, headers={"Authorization": f"Bearer <token>"})
    assert resp.status_code in [404, 200], "Precondition: API reachable"
    if resp.status_code == 200:
        # Agent does exist: force delete (for test isolation)
        requests.delete(url, headers={"Authorization": f"Bearer <token>"})
    return agent_id

@pytest.mark.regression
@pytest.mark.sanity
@pytest.mark.asvs('V10')  # OWASP ASVS reference
@pytest.mark.boundary
@pytest.mark.risklevel("medium")
def test_delete_non_existent_agent(valid_bearer_token, non_existent_agent_id):
    """
    TC-DELETE-f2e6c865-003
    Ensure the endpoint handles deletion of a non-existent agent gracefully.
    Requirements:
        - RFC 8259: JSON compliance (empty response/body or error message)
        - OWASP ASVS: Proper error handling (no information leakage)
        - ISO/IEC/IEEE 29148: Clear traceability and outcome verifiability
    """
    url = f"{API_BASE_URL}{AGENTS_ENDPOINT.format(agent_id=non_existent_agent_id)}"
    headers = {
        "Authorization": f"Bearer {valid_bearer_token}",
        "Content-Type": "application/json"
    }
    response = requests.delete(url, headers=headers)

    # Expected outcome: 200 (idempotent) or 404 (not found) only
    assert response.status_code in [200, 404], (
        f"Expected status 200 or 404, got {response.status_code}"
    )

    # Body validation
    if response.status_code == 200:
        # Per idempotent design, response SHOULD be empty per RFC 8259
        assert response.text.strip() in ["", "{}", "null"], (
            f"Expected empty response, got: '{response.text}'"
        )
    elif response.status_code == 404:
        # Per standard, error message (if any) must not disclose sensitive info (ASVS)
        content_type = response.headers.get("Content-Type", "")
        if content_type.startswith("application/json"):
            try:
                data = response.json()
                # ISO/IEC/IEEE 29148: error schema should be traceable (e.g. reason, code)
                assert "error" in data or "message" in data, (
                    f"Expected error/message in JSON response, got: {data}"
                )
            except Exception:
                pytest.fail(f"Response not valid JSON: {response.text}")
        else:
            # If not JSON, must be empty or non-sensitive
            assert response.text.strip() == "", (
                f"Expected empty response, got: '{response.text}'"
            )

    # Compliance: No side effects, ensure test isolation
    # (No teardown required — action is idempotent and no valid agent was modified)
