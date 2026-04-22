import pytest
import requests

API_BASE_URL = "https://api.example.com"  # Replace with the target API base URL if needed

@pytest.fixture(scope="module")
def agent_id():
    # Setup: Replace with a fixture or mechanism to retrieve a valid agent_id from your test data/environment
    # Requirements traceability: ISO/IEC/IEEE 29148 §6.4.10 (Test Setup and Execution), RFC 8259 (JSON API usage), OWASP ASVS V2 (Authentication enforcement)
    return "<REPLACE_WITH_AGENT_ID>"  # The test assumes agent exists as per preconditions


def test_delete_agent_without_auth_header(agent_id):
    """
    TestCase ID: TC-DELETE-f2e6c865-001
    Description: Ensure the endpoint returns an authentication error when the Authorization header is missing.
    Compliance: OWASP ASVS V2 (Authentication and Session Management), V10 (Error Handling), RFC 8259 (JSON), ISO/IEC/IEEE 29148 (Traceable, Verifiable Requirement)
    """
    url = f"{API_BASE_URL}/api/agents/{agent_id}"
    headers = {
        "Content-Type": "application/json"
        # Authorization header intentionally omitted as per test steps
    }
    response = requests.delete(url, headers=headers)
    
    # Validation per expected results
    # Assert status code is 401 (RFC 8259-compliant error handling, OWASP ASVS V2)
    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code} (ASVS V2, V10)"

    # Assert response body is valid JSON (RFC 8259)
    try:
        resp_json = response.json()
    except Exception as e:
        pytest.fail(f"Response is not valid JSON: {e} (RFC 8259)")

    # Assert response schema contains 'detail' field (ISO/IEC/IEEE 29148, OWASP ASVS V10)
    assert "detail" in resp_json, "Response missing 'detail' field indicating authentication error (ASVS V10)"
    assert isinstance(resp_json["detail"], str), "'detail' field must be a string (ISO/IEC/IEEE 29148, RFC 8259)"
    # Assert error message indicates authentication failure
    assert "auth" in resp_json["detail"].lower(), "Error message should indicate authentication failure (ASVS V2, V10)"

# No teardown required since agent is not deleted (no authorization)
