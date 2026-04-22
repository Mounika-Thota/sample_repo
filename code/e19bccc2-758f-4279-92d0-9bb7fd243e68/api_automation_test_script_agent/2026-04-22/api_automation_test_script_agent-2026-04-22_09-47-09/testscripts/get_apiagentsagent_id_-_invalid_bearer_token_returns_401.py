import pytest
import requests

BASE_URL = "https://api.example.com"  # Replace with your base API URL
def get_existing_agent_id():
    # Placeholder: Implement a reliable way (fixture or API) to get a valid agent ID for security/negative tests.
    # e.g., via environment variables, config, or setup a known agent as part of test hygiene.
    # This function should NOT create or modify state, to respect negative and idempotent testing.
    # For this compliance-focused test, we raise if agent ID cannot be supplied.
    agent_id = pytest.config.getoption("--agent-id", default=None)
    if not agent_id:
        raise RuntimeError("Agent ID must be supplied using --agent-id option for compliance and traceability.")
    return agent_id

@pytest.fixture(scope="module")
def agent_id():
    return get_existing_agent_id()

@pytest.mark.security
@pytest.mark.negative
@pytest.mark.asvs("V2")
@pytest.mark.risk("high")
def test_get_agent_with_invalid_token(agent_id):
    """
    TC-GET-ab9c4c2e-003
    Verify that using an invalid or expired Bearer token results in an unauthorized (401) response.
    Requirements Traceability:
        - RFC 8259: All JSON responses MUST be standard JSON.
        - OWASP ASVS V2: Authentication and session management failures should result in HTTP 401.
        - ISO/IEC/IEEE 29148: Each expected result is verifiable and linked to a test step.
    Preconditions:
      - API is reachable.
      - An agent with the provided ID exists and is accessible by a valid token.
    """
    endpoint = f"{BASE_URL}/api/agents/{agent_id}"
    headers = {
        "Authorization": "Bearer INVALIDTOKEN",
        "Accept": "application/json"
    }
    response = requests.get(endpoint, headers=headers)

    # ASVS V2, ISO/IEC/IEEE 29148 TRACEABILITY
    # 1. Status code MUST be 401.
    assert response.status_code == 401, f"Expected HTTP 401, got {response.status_code} ({response.text})"

    # 2. Content-Type header MUST be JSON per RFC 8259.
    assert response.headers.get('Content-Type', '').startswith('application/json'), (
        f"Expected 'Content-Type: application/json', got {response.headers.get('Content-Type')}"
    )

    # 3. RFC 8259: Response MUST be valid JSON. Error message MUST indicate token issue.
    try:
        body = response.json()
    except Exception as e:
        pytest.fail(f"Response is not valid JSON (required by RFC 8259): {e}")

    # The error message should indicate invalid/expired token; flexible to API, but MUST NOT leak implementation/system details.
    assert any(keyword in (body.get('error') or body.get('message') or '').lower() for keyword in ["invalid token", "expired token", "unauthorized", "authentication"]), (
        f"Error message should state the token is invalid, expired, or unauthorized. Received: {body}"
    )
