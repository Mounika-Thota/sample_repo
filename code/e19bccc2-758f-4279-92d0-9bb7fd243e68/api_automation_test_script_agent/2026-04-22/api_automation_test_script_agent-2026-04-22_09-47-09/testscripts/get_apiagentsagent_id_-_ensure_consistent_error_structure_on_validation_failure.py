import pytest
import requests

# Test Configuration, aligning with RFC 8259 (JSON), OWASP ASVS (V10: Error Handling), ISO/IEC/IEEE 29148 (Requirements Traceability)
BASE_URL = "https://api.example.com"  # Replace with actual API base URL

@pytest.fixture(scope="session")
def api_token():
    """
    Fixture to provide a valid token for authentication. Complies with ISO/IEC/IEEE 29148 requirements for setup.
    """
    # The token must be provisioned securely (not hardcoded here, see compliance note)
    # Example: Load from environment or a secure vault
    token = "<REPLACE_WITH_TOKEN>"
    assert token and token.startswith("ey"), "Token must be valid"
    return token

@pytest.fixture(scope="function")
def base_headers(api_token):
    """
    Fixture for base request headers.
    """
    return {
        "Authorization": f"Bearer {api_token}",
        "Accept": "application/json"
    }

# Traceability Matrix
REQUIREMENTS_TRACE = {
    "RFC8259": "Ensures JSON encoding and decoding and proper structure.",
    "OWASP_ASVS_V10": "Error responses must not leak sensitive information. Validation error must be clearly structured.",
    "ISO_29148": "Each verification step is traced to a user/system requirement."
}

@pytest.mark.regression
@pytest.mark.sanity
@pytest.mark.usability
@pytest.mark.owasp_asvs_v10
@pytest.mark.iso_29148
@pytest.mark.rfc8259
@pytest.mark.traceability(REQUIREMENTS_TRACE)
def test_agent_get_422_validation_error(base_headers):
    """
    TC-GET-ab9c4c2e-008: Validate that 422 responses comply with HTTPValidationError schema and contain appropriate detail, msg, and type.
    Requirements: RFC 8259, OWASP ASVS (V10), ISO/IEC/IEEE 29148
    """
    # Step 1: Send GET request to /api/agents/@@BAD@@ (invalid agent_id)
    bad_agent_id = "@@BAD@@"
    endpoint = f"{BASE_URL}/api/agents/{bad_agent_id}"
    response = requests.get(endpoint, headers=base_headers)

    # Step 2: Validate Status 422 (Unprocessable Entity)
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"  # OWASP ASVS V10: Don't disclose unnecessary info

    # Step 3: Validate error structure in response, RFC 8259 compliant JSON
    try:
        resp_json = response.json()
    except Exception as e:
        pytest.fail(f"Response is not valid JSON as per RFC 8259: {str(e)}")

    assert 'detail' in resp_json, "Response JSON must contain 'detail' field (ISO 29148, traceable to error reporting requirement)"
    assert isinstance(resp_json['detail'], list), "'detail' must be a list (RFC 8259 compliance)"
    for item in resp_json['detail']:
        assert isinstance(item, dict), "Each item in 'detail' must be a dict"
        # ISO/IEC/IEEE 29148: Each expected key is verified
        assert 'loc' in item, "Each detail item must contain 'loc' (requirement traceable: error localization)"
        assert isinstance(item['loc'], list), "'loc' must be a list"
        # ISO/IEC/IEEE 29148: 'msg' field type and existence
        assert 'msg' in item, "Each detail item must contain 'msg' (requirement: error description)"
        assert isinstance(item['msg'], str), "'msg' must be a string"
        # OWASP ASVS: 'type' for error classification
        assert 'type' in item, "Each detail item must contain 'type' (requirement: error type/class)"
        assert isinstance(item['type'], str), "'type' must be a string"

    # Ensure no sensitive information is leaked (OWASP ASVS V10)
    # example: agent_id value must not be echoed back or internal error dumps
    for item in resp_json['detail']:
        assert bad_agent_id not in item.get('msg', ''), "Error message should not echo input or sensitive info"

    # Requirement traceability logging
    print(f"Traceability: {REQUIREMENTS_TRACE}")

# No teardown necessary (stateless GET, no resource mutation)