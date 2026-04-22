import pytest
import requests

BASE_URL = 'https://api.example.com'  # Replace with actual base URL

@pytest.fixture(scope="module")
def bearer_token():
    """
    Retrieve or provide a valid Bearer token for authentication.
    This fixture enforces proper session management per ISO/IEC/IEEE 29148 and OWASP ASVS controls.
    """
    # Replace with code to retrieve valid token
    # E.g., via oauth/token endpoint or config
    token = '<REPLACE_WITH_TOKEN>'
    assert token and isinstance(token, str), "Bearer token must be non-empty string for RFC 8259 compliance."
    return token

@pytest.fixture(scope="module")
def agent_id():
    """
    Ensure a valid agent exists and return its ID. If none exists, create one and return its ID.
    Compliant with requirements for test independence and traceability.
    """
    # Implement logic to ensure agent exists or create one, then yield the agent_id
    agent_id = '<REPLACE_WITH_AGENT_ID>'
    assert agent_id, "Precondition failed: Valid agent ID is required."
    yield agent_id
    # Optional: Add teardown logic for cleanup if agent was created

@pytest.mark.regression
@pytest.mark.owasp_asvs(['V5', 'V10'])
def test_update_agent_fields_null(bearer_token, agent_id):
    """
    Validate updating an agent with all fields set to null is accepted if supported (RFC 8259, ISO/IEC/IEEE 29148 TR).
    Traceability: Testcase ID TC-PUT-55cdd53a-003.
    """
    url = f"{BASE_URL}/api/agents/{agent_id}"
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    # All fields explicitly set to JSON null
    payload = {
        "slug": None,
        "display_name": None,
        "category": None,
        "description": None,
        "parent_id": None
    }
    
    # Ensure outgoing payload is RFC 8259 compliant JSON
    response = requests.put(url, headers=headers, json=payload)

    # Validate status code (expecting 200)
    assert response.status_code == 200, (
        f"Expected HTTP 200 OK, got {response.status_code}. Response: {response.text}"
    )  # ISO/IEC/IEEE 29148 traceability: expected_results[0]

    # Validate content type (RFC 8259, OWASP ASVS V10)
    resp_content_type = response.headers.get('Content-Type', '')
    assert resp_content_type.startswith('application/json'), (
        f"Content-Type must be application/json, got '{resp_content_type}'"
    )  # expected_results[1]
    
    # Validate JSON response body is present and parseable (RFC 8259)
    try:
        resp_json = response.json()
        assert isinstance(resp_json, dict), "Response body must be a JSON object (RFC 8259)"
    except Exception as e:
        pytest.fail(f"Response body is not valid JSON: {e}; raw: {response.text}")
    # Optionally: validate presence of keys, response schema compliance as per 'expected_response_schema'

    # Traceability: Test ID TC-PUT-55cdd53a-003, OWASP ASVS mapping V5, V10
