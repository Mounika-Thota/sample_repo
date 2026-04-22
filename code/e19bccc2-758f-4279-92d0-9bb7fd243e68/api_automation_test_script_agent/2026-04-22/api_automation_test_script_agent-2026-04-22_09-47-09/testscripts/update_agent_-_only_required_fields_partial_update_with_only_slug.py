import pytest
import requests

API_BASE_URL = "https://api.example.com"  # Replace with actual API base URL
def get_valid_token():
    # Placeholder for actual token retrieval logic
    # Ensure token retrieval mechanism complies with RFC 8259 and OWASP ASVS guidelines
    return "<REPLACE_WITH_TOKEN>"

def get_existing_agent_id():
    # Placeholder for actual agent ID retrieval logic (should return a valid agent id from system under test)
    return "<REPLACE_WITH_AGENT_ID>"

@pytest.fixture(scope="module")
def auth_token():
    token = get_valid_token()
    assert token is not None and len(token) > 0, "Bearer token should be valid per OWASP ASVS V2 requirements"
    return token

@pytest.fixture(scope="module")
def existing_agent_id():
    agent_id = get_existing_agent_id()
    assert agent_id is not None and len(agent_id) > 0, "Agent must exist per precondition"
    return agent_id

@pytest.mark.regression
@pytest.mark.sanity
@pytest.mark.functional
def test_update_agent_slug_only(auth_token, existing_agent_id):
    """Validate that agent can be updated with only the slug field set (others omitted)."""
    url = f"{API_BASE_URL}/api/agents/{existing_agent_id}"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    body = {"slug": "agent-update-slug"}  # Per RFC 8259, enforce minimal JSON

    response = requests.put(url, headers=headers, json=body)

    # Assert status code compliance per expected results and OWASP ASVS V5
    assert response.status_code == 200, f"Expected status 200 but got {response.status_code}"

    # Assert response content-type compliance (RFC 8259, ISO/IEC/IEEE 29148)
    # Allow for parameters but must contain application/json
    content_type = response.headers.get("Content-Type", "")
    assert "application/json" in content_type.lower(), "Response Content-Type must be application/json as per RFC 8259"

    # Validate response body is valid JSON per RFC 8259
    try:
        response_json = response.json()
    except Exception as e:
        pytest.fail(f"Response body is not valid JSON: {e}")

    # ISO/IEC/IEEE 29148: Check response traceability and mandatory fields if needed
    assert isinstance(response_json, dict), "Response JSON must be an object as per RFC 8259 and functional spec"

    # Optionally, OWASP ASVS: Check for absence of sensitive fields
    for field in ["password", "secret", "token"]:
        assert field not in response_json, f"Sensitive field '{field}' should not be present in response"

    # Additional compliance checks (extension point)

    # (No teardown needed, data is updated only)
