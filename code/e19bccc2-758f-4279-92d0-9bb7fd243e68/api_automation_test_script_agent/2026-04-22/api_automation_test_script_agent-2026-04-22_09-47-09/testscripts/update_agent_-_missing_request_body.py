import pytest
import requests
from jsonschema import validate, ValidationError

# Compliance traceability: RFC 8259 (valid JSON), OWASP ASVS (V5, V10: error handling, input validation), ISO/IEC/IEEE 29148 (requirements verification)

BASE_URL = "https://api.example.com"  # Replace with actual API base URL
AGENT_ID = "<REPLACE_WITH_AGENT_ID>"  # Must be replaced by valid agent id from test setup
BEARER_TOKEN = "<REPLACE_WITH_TOKEN>"  # Must be replaced by valid token from test setup

@pytest.fixture(scope="module")
def auth_header():
    """Setup for Authorization Header."""
    return {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }

@pytest.fixture(scope="module")
def agent_id():
    """Setup for Agent ID. Ensure agent exists prior to test execution."""
    return AGENT_ID

# RFC 8259: The response must be valid JSON
# OWASP ASVS V5, V10: Ensure error handling and input validation are enforced
# ISO/IEC/IEEE 29148: Requirements traceable via test case ID and metadata

VALIDATION_ERROR_SCHEMA = {
    "type": "object",
    "properties": {
        "detail": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "loc": {
                        "type": "array",
                        "items": { "type": ["string", "integer"] }
                    },
                    "msg": { "type": "string" },
                    "type": { "type": "string" }
                },
                "required": ["loc", "msg", "type"]
            }
        }
    },
    "required": ["detail"]
}

@pytest.mark.regression
@pytest.mark.owasp_asvs(["V5", "V10"])
def test_put_agent_without_body_returns_422(auth_header, agent_id):
    """TC-PUT-55cdd53a-009: Validate update returns 422 Unprocessable Entity if JSON body is missing."""
    url = f"{BASE_URL}/api/agents/{agent_id}"

    # Send PUT request without body
    response = requests.put(url, headers=auth_header)

    # Assert: Status 422
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    # Assert: RFC 8259 - response must be valid JSON
    try:
        resp_json = response.json()
    except ValueError as e:
        pytest.fail(f"Response not valid JSON: {e}")

    # Assert: Error response conforms to validation error schema (OWASP ASVS)
    try:
        validate(instance=resp_json, schema=VALIDATION_ERROR_SCHEMA)
    except ValidationError as e:
        pytest.fail(f"Response schema validation failed: {str(e)}")

    # Assert: Error message and type are present and sensible
    details = resp_json.get("detail", [])
    assert len(details) > 0, "Error detail missing or empty"
    for item in details:
        assert "loc" in item and "msg" in item and "type" in item, "Error item missing required fields"
        assert isinstance(item["msg"], str) and item["msg"], "Error msg should be non-empty string"
        assert isinstance(item["type"], str) and item["type"], "Error type should be non-empty string"

    # Compliance references
    # - RFC 8259: valid JSON in request and response
    # - OWASP ASVS: V5 input validation, V10 error handling
    # - ISO/IEC/IEEE 29148: test ID and traceable requirements

# Note: No teardown required (no persistent changes to agent data)
