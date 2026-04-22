import pytest
import requests

API_BASE_URL = "https://<REPLACE_WITH_API_BASE_URL>"
ENDPOINT = "/api/agents/"
EXPECTED_STATUS_CODE = 200

@pytest.fixture(scope="session")
def api_token():
    # Placeholder: retrieve valid Bearer token securely
    # Ensure your authentication scheme follows RFC 8259 for JSON and OWASP ASVS V5/V10 compliance
    # Token retrieval implementation should enforce ISO/IEC/IEEE 29148 traceability
    token = "<REPLACE_WITH_TOKEN>"
    assert token, "Token must not be empty (ASVS V5 requirement)."
    return token

@pytest.fixture(scope="function")
def api_headers(api_token):
    return {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

@pytest.fixture(scope="function")
def cleanup_agent():
    # Setup for cleanup, keep traceability for each agent created
    created_agents = []
    yield created_agents
    # Teardown: If agent IDs exist, remove them as per ISO/IEC/IEEE 29148 lifecycle
    for agent_id in created_agents:
        requests.delete(f"{API_BASE_URL}{ENDPOINT}{agent_id}", headers={"Authorization": f"Bearer <REPLACE_WITH_TOKEN>"})

@pytest.mark.regression
@pytest.mark.boundary
@pytest.mark.owasp_asvs(['V5', 'V10'])
def test_post_agents_accepts_null_description_and_parent_id(api_headers, cleanup_agent):
    """Validate POST /api/agents/ accepts null values for 'description' and 'parent_id'."""
    # Ensure API is reachable, complying with ASVS V10 for error handling
    try:
        health = requests.get(f"{API_BASE_URL}/health", headers=api_headers)
        assert health.status_code == 200, f"API not reachable: {health.status_code}"  # ISO/IEC/IEEE 29148 traceability
    except Exception as e:
        pytest.fail(f"API health check failed: {str(e)}")
    payload = {
        "description": None,
        "parent_id": None
    }
    response = requests.post(f"{API_BASE_URL}{ENDPOINT}", headers=api_headers, json=payload)
    assert response.status_code == EXPECTED_STATUS_CODE, (
        f"Expected status {EXPECTED_STATUS_CODE}, got {response.status_code} (OWASP ASVS V5)."
    )
    resp_json = response.json()
    # ISO/IEC/IEEE 29148: All requirements are verifiable (fields are null if input is null)
    assert 'description' in resp_json, "'description' missing in response (RFC 8259, property presence)."
    assert resp_json['description'] is None, (
        "'description' must be null in response per RFC 8259 and requirements traceability."
    )
    assert 'parent_id' in resp_json, "'parent_id' missing in response (RFC 8259, property presence)."
    assert resp_json['parent_id'] is None, (
        "'parent_id' must be null in response per RFC 8259 and requirements traceability."
    )
    agent_id = resp_json.get('id')
    assert agent_id, "Agent 'id' missing in response (ISO/IEC/IEEE 29148: verifiable requirement)."
    cleanup_agent.append(agent_id)  # For lifecycle traceability
