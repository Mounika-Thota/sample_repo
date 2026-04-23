import pytest
import requests

BASE_URL = "https://api.example.com"  # Replace with actual base URL
\****************(scope="session")
def valid_bearer_token():
    """Fixture to provide a valid Bearer token.
    In compliance with OWASP ASVS V5 (Authentication, Session Management) and ISO/IEC/IEEE 29148, ensure token retrieval is secure and not hardcoded.
    """
    # TODO: Implement secure token retrieval, possibly from environment/secrets store.
    # For illustration only:
    token = "<REPLACE_WITH_TOKEN>"
    assert token and token != "<REPLACE_WITH_TOKEN>", "Bearer token must be provided via a secure mechanism."
    return token

def is_rfc8259_json(response):
    """Check response Content-Type and parse-ability with strict RFC8259 compliance."""
    assert response.headers.get('Content-Type', '').startswith('application/json'), "Content-Type must be application/json (RFC 8259 section 11)."
    try:
        resp_json = response.json()
    except ValueError:
        pytest.fail("Response body is not valid RFC 8259 JSON.")
    return resp_json

def validate_asvs_error_schema(detail):
    """Ensure error details match the schema as per OWASP ASVS V10 and provided OpenAPI spec."""
    assert isinstance(detail, list), "'detail' must be an array as per API contract and RFC 8259."
    for entry in detail:
        assert isinstance(entry, dict), "Each entry in 'detail' must be an object per RFC 8259."
        # 'loc' must be a list of strings/integers
        assert 'loc' in entry, "Validation error detail must include 'loc' field. (ASVS V10, ISO/IEC/IEEE 29148:6.4.4)"
        assert isinstance(entry['loc'], list) and all(isinstance(item, (str, int)) for item in entry['loc']), "'loc' must be a list of strings/ints."
        # 'msg' must be a string
        assert 'msg' in entry and isinstance(entry['msg'], str), "'msg' must be a string."
        # 'type' must be a string
        assert 'type' in entry and isinstance(entry['type'], str), "'type' must be a string."
\************************\**********************\******************('V5', 'V10')  # traceability to OWASP ASVS controls\*************.owasp_asvs_refs(['V5', 'V10'])
def test_get_agent_invalid_agentid_validation(valid_bearer_token):
    """
    TC-GET-2e2e0c6c-006: Validate that GET /api/agents/{agent_id} with invalid agent_id format returns HTTP 422 with validation error.
    Requirements compliance: RFC8259 (JSON), OWASP ASVS (V5, V10), ISO/IEC/IEEE 29148 (requirements traceability).
    """
    # Preconditions: API is reachable
    endpoint = f"{BASE_URL}/api/agents/!@#$%"  # Deliberate invalid id with special characters
    headers = {"Authorization": f"Bearer {valid_bearer_token}"}

    response = requests.get(endpoint, headers=headers)

    # 1. Validate status code == 422
    assert response.status_code == 422, f"Expected HTTP 422, got {response.status_code}"

    # 2. Validate response body is RFC 8259 compliant JSON, and schema matches expectation
    resp_json = is_rfc8259_json(response)

    assert 'detail' in resp_json, "'detail' field must be present in the response body (ASVS V10)."
    validate_asvs_error_schema(resp_json['detail'])
