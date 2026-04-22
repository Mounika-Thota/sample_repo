import pytest
import requests

BASE_URL = "https://api.example.com"  # Replace with actual base URL
def get_existing_agent_id():
    # This function should implement a reliable way to retrieve a valid agent ID.
    # It must not use hardcoded or dummy data; implementation depends on your environment.
    # Example: Fetch from a fixture, environment var, or a setup endpoint.
    raise NotImplementedError("Implement agent ID retrieval as per deployment/context.")

@pytest.fixture(scope="module")
def agent_id():
    return get_existing_agent_id()

def test_get_agent_without_auth_header(agent_id):
    """
    TC-GET-ab9c4c2e-002: Verify that omitting the Bearer token
    in the Authorization header results in a 401 Unauthorized response.
    Compliance: RFC 8259, OWASP ASVS (V2), ISO/IEC/IEEE 29148
    """
    endpoint = f"{BASE_URL}/api/agents/{agent_id}"
    # Standard as per RFC 8259 for application/json
    headers = {
        "Accept": "application/json"
    }
    response = requests.get(endpoint, headers=headers)
    
    # Validate Unauthorized HTTP status code (OWASP ASVS V2)
    assert response.status_code == 401, (
        f"Expected HTTP 401 Unauthorized, got {response.status_code}."
    )
    
    # Validate Content-Type is JSON as per RFC 8259
    assert response.headers.get('Content-Type', '').startswith("application/json"), (
        f"Expected Content-Type 'application/json', got '{response.headers.get('Content-Type')}'."
    )

    # Validate error message indicates authentication required (traceable, ISO/IEC/IEEE 29148)
    try:
        response_json = response.json()
    except ValueError:
        pytest.fail(f"Response body is not valid JSON: {response.text}")

    expected_keywords = ['auth', 'token', 'login', 'credential', 'unauth']
    
    # At least one keyword must appear in a top-level value (OWASP ASVS V2, traceability)
    message = ''
    if isinstance(response_json, dict):
        message = ' '.join(str(value).lower() for value in response_json.values())
    elif isinstance(response_json, list):
        message = ' '.join(str(item).lower() for item in response_json)
    match = any(keyword in message for keyword in expected_keywords)
    assert match, (
        "Error message does not clearly indicate that authentication is required. "
        f"Response content: {response_json}"
    )
