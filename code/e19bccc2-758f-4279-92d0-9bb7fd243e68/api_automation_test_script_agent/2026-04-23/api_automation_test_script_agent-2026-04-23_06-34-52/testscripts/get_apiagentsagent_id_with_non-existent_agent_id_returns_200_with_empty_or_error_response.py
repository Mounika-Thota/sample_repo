import pytest
import requests

# Constants (replace with actual values or use fixtures/secrets management in a real project)
API_BASE_URL = "https://api.example.com"  # Should NOT be hardcoded in prod! Use configs/env variables.

# Sample utility function for token injection (modify for secure management)
def get_bearer_token():
    # Retrieve a valid token from secure storage or fixture
    # Placeholder for demonstration purposes only
    return "<REPLACE_WITH_TOKEN>"
\****************(scope="module")
def auth_headers():
    """
    Prepare Authorization header with valid Bearer token.
    RFC 8259: Ensure headers are correctly formatted (no null bytes, proper field/value structure)
    Traceability: Precondition 'Valid Bearer token is available' (ISO/IEC/IEEE 29148)
    """
    token = get_bearer_token()
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
\****************(scope="function")
def non_existent_agent_id():
    """
    Returns a value highly likely NOT to exist as an agent_id.
    This must be implementation-aware; ideally, generate an agent_id and verify its nonexistence if possible.
    Traceability: 'Agent with ID <NON_EXISTENT_AGENT_ID> does not exist' (ISO/IEC/IEEE 29148)
    """
    return "2e2e0c6c-nonexistent-test-agent"
\*************.owasp_v10\************************\**********************\********************\*****************
class TestGetAgentNegative:
    """
    TestCase ID: TC-GET-2e2e0c6c-004
    Description: Validate GET /api/agents/{agent_id} with non-existent agent_id returns HTTP 200 w/ empty or error or 404 depending on implementation.
    Compliance: RFC 8259 (JSON), OWASP ASVS V10 (Error Handling), ISO/IEC/IEEE 29148 (Traceability)
    """

    def test_get_nonexistent_agent(self, auth_headers, non_existent_agent_id):
        """
        Steps:
         1. Send GET request to /api/agents/<NON_EXISTENT_AGENT_ID> with Authorization header.
        Validations:
         - Status code is 200 OR 404 (per spec)
         - Response body is empty OR contains a standard error message (ASVS-aligned)
        """
        endpoint = f"{API_BASE_URL}/api/agents/{non_existent_agent_id}"
        response = requests.get(endpoint, headers=auth_headers)

        # Compliance: Verify allowed status codes
        assert response.status_code in [200, 404], \
            f"Expected 200 or 404 for non-existent agent, got {response.status_code} (OWASP ASVS V10.5, ISO/IEC/IEEE 29148)"

        try:
            json_body = response.json()
        except ValueError:
            json_body = None

        # Compliance: RFC 8259 requires valid/empty JSON or empty response.
        if response.status_code == 200:
            # Implementation 1: empty body, or empty JSON, or optional error structure
            assert json_body == {} or json_body is None or json_body == [], \
                "Expected empty JSON body, empty array/object, or no content for 200 on non-existent agent (RFC 8259, ISO/IEC/IEEE 29148)"
        elif response.status_code == 404:
            # Implementation 2: error message (ASVS V10.4.1: Error message does not leak sensitive info)
            # Expected minimal error structure: {"error": "not found"} or similar
            assert isinstance(json_body, dict), "Expected error response to be a JSON object (RFC 8259)"
            assert any(key in json_body for key in ["error", "message", "detail"]), \
                "404 response should include a user-consumable error key per ASVS V10"
            # Ensure error messages do not disclose implementation, IDs, stack traces, etc.
            error_message = str(json_body.get("error") or json_body.get("message") or json_body.get("detail") or "")
            assert not any(x in error_message.lower() for x in ["exception", "trace", "stack", "sql", "password", "internal"]), \
                f"Error message leaks implementation detail: {error_message} (ASVS V10.4.1, ISO/IEC/IEEE 29148)"
