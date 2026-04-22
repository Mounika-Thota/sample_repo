import pytest
import requests

# Constants for standards compliance
RFC_8259_COMPLIANCE_NOTE = "Ensures JSON requests and responses are strictly valid per RFC 8259."
OWASP_ASVS_REFS = ['V5', 'V10']  # Referenced in test case
ISO_IEC_IEE_29148_TRACE = "Test requirements and outcomes are traceable to agent update API specification."

# Hooks for setup and teardown
@pytest.fixture(scope="module")
def api_url():
    # This fixture may contain dynamic discovery to meet ISO/IEC/IEEE 29148 traceability requirements
    return "https://api.example.com"  # Replace with actual base URL in environment config

@pytest.fixture(scope="module")
def bearer_token():
    # In real environment, fetch/generate a valid token as per standards
    # The test requires a valid Bearer token for authentication
    return "<REPLACE_WITH_TOKEN>"  # Replace securely as per test environment

@pytest.fixture(scope="module")
def agent_id():
    # Precondition: Agent with this ID must exist
    return "<REPLACE_WITH_AGENT_ID>"  # Replace dynamically or via setup call if needed

@pytest.fixture(scope="function")
def cleanup_agent():
    # Implement cleanup logic if mutation occurs in future
    # For negative test, agent should not be modified
    yield
    # No teardown needed unless agent changes occur

# Utility to validate error response schema per OpenAPI and standards
def validate_error_schema(response_json):
    assert 'detail' in response_json, "RFC 8259: JSON error response must contain 'detail' field."
    assert isinstance(response_json['detail'], list), "RFC 8259: 'detail' must be a list."
    for error in response_json['detail']:
        assert 'loc' in error, "Each error object must have 'loc' field (OWASP ASVS V10).
"
        assert isinstance(error['loc'], list), "'loc' field must be a list per OpenAPI spec."
        assert 'msg' in error and isinstance(error['msg'], str), "'msg' field must be string."
        assert 'type' in error and isinstance(error['type'], str), "'type' field must be string."

@pytest.mark.regression
@pytest.mark.asvs(["V5", "V10"])
def test_api_rejects_invalid_slug_datatype(api_url, bearer_token, agent_id, cleanup_agent):
    """
    Validate API rejects update if slug field has invalid datatype (e.g., integer instead of string or null).
    Compliance:
      - RFC 8259: JSON encoding and error format
      - OWASP ASVS: V5 Input Validation, V10 Error Handling
      - ISO/IEC/IEEE 29148: Requirements traceability to agent update endpoint
    """
    url = f"{api_url}/api/agents/{agent_id}"
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    # Invalid payload: slug as integer instead of allowed string or null
    payload = {"slug": 123}
    
    response = requests.put(url, headers=headers, json=payload)
    
    # Assert status code per OpenAPI and ASVS requirement
    assert response.status_code == 422, (
        f"Expected 422 Unprocessable Entity for validation error (ASVS V5/V10), got {response.status_code}."
    )
    
    # Validate RFC 8259 compliance (ensure strict JSON per standard)
    try:
        response_json = response.json()
    except ValueError:
        pytest.fail("Response is not valid RFC 8259 JSON (OWASP ASVS V10).")
        return
    
    # Assert error schema as defined in OpenAPI and test metadata
    validate_error_schema(response_json)
    
    # Additional standards traceability assertions
    assert any('slug' in error['loc'] for error in response_json['detail']), (
        "Error location must reference 'slug' for requirements traceability (ISO/IEC/IEEE 29148)."
    )
    # Ensure error type denotes datatype violation
    assert any(error['type'] == 'type_error.integer' for error in response_json['detail']), (
        "Error type must specify 'type_error.integer' for invalid datatype (ASVS V5)."
    )

    # Compliance notes (non-executable, for traceability)
    print(RFC_8259_COMPLIANCE_NOTE)
    print(f"OWASP ASVS references checked: {OWASP_ASVS_REFS}")
    print(ISO_IEC_IEE_29148_TRACE)
