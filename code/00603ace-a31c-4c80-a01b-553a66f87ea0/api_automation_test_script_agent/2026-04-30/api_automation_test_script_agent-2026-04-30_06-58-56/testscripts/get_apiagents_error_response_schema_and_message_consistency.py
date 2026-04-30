import pytest
import requests

def get_bearer_token():
    # Token should be retrieved securely or injected via environment/configuration
    # For compliance: NEVER hardcode sensitive credentials (OWASP ASVS V2)
    # Replace with secure fetching, e.g., from env: os.environ["API_BEARER_TOKEN"]
    raise NotImplementedError("Bearer token retrieval not implemented. Please provide a secure implementation.")
\****************(scope="module")
def api_base_url():
    # ISO/IEC/IEEE 29148: External interfaces must be configurable
    return "<REPLACE_WITH_API_BASE_URL>"
\****************(scope="module")
def auth_header():
    token = get_bearer_token()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def validate_http_validation_error_schema(response_json):
    # RFC 8259: JSON structure validation
    # OWASP ASVS V10: Error handling and information leakage compliance
    assert "detail" in response_json, "Missing 'detail' in error response. [ASVS V10]"
    assert isinstance(response_json["detail"], list), "'detail' must be a list. [RFC 8259]"
    error_found = False
    for detail in response_json["detail"]:
        assert isinstance(detail, dict), "Each detail item should be a dict/object. [RFC 8259]"
        required_keys = {"loc", "msg", "type"}
        assert required_keys.issubset(detail.keys()), (
            f"Error detail missing keys: {required_keys - set(detail.keys())} [ISO/IEC/IEEE 29148]"
        )
        if (
            detail["loc"] == ["query", "skip"] and
            detail["msg"] == "value is not a valid integer" and
            detail["type"] == "type_error.integer"
        ):
            error_found = True
    assert error_found, (
        "Error response must clearly identify that 'skip' is the invalid parameter with a type error. [ISO/IEC/IEEE 29148][OWASP ASVS V5]"
    )
\************************\*************.input_validation\*************.owasp_asvs(["V5", "V10"])
def test_get_agents_invalid_skip_parameter(api_base_url, auth_header):
    """
    TC-GET-feb8d5e2-09: Validate that error responses for GET /api/agents/ (e.g., 422) conform to HTTPValidationError schema and provide meaningful messages.
    Traceability:
    - ISO/IEC/IEEE 29148: Requirements traceability for error schema
    - RFC 8259: JSON error schema
    - OWASP ASVS V5: Input validation
    - OWASP ASVS V10: Error handling
    """
    endpoint = f"{api_base_url}/api/agents/"
    params = {"skip": "abc"}  # Invalid: should be an integer
    response = requests.get(endpoint, headers=auth_header, params=params)

    # Validate status code
    assert response.status_code == 422, (
        f"Expected status code 422 for invalid 'skip'. Got {response.status_code} [OWASP ASVS V5]"
    )

    # Parse and validate response schema and error message
    try:
        response_json = response.json()
    except ValueError:
        pytest.fail("Response is not valid JSON. [RFC 8259]")
    validate_http_validation_error_schema(response_json)