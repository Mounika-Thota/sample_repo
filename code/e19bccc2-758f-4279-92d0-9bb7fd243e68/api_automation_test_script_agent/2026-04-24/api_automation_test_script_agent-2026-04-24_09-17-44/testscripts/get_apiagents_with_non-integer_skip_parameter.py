import pytest
import requests

def get_valid_bearer_token():
    # Placeholder for secure retrieval of a valid token
    # Replace with secure retrieval in actual implementation per RFC 8259/OWASP ASVS guidelines
    raise NotImplementedError("Replace with secure token retrieval logic as per org standards.")

def is_valid_validation_error(response_json):
    """
    Validates the structure of the error response as per expected schema.
    Reference OWASP ASVS V5, V10
    """
    if not isinstance(response_json, dict):
        return False
    detail = response_json.get('detail')
    if not isinstance(detail, list) or not detail:
        return False
    for err in detail:
        if not isinstance(err, dict):
            return False
        # RFC8259: All keys are strings, values can be of various types. IS0 29148: Schema traceable.
        if not all(key in err for key in ('loc', 'msg', 'type')):
            return False
        if not isinstance(err['loc'], list):
            return False
        # We don't enforce loc members' types since OpenAPI allows heterogeneous loc values.
        if not isinstance(err['msg'], str):
            return False
        if not isinstance(err['type'], str):
            return False
    return True
\****************(scope="module")
def api_base_url():
    # Should be set according to deployment environment
    # ISO/IEC/IEEE 29148: requirements traceability - keep endpoint configurable.
    return "https://api.example.com"  # Replace with actual API URL
\****************(scope="module")
def auth_header():
    token = None
    try:
        token = get_valid_bearer_token()
    except NotImplementedError:
        pytest.skip("Valid Bearer token retrieval not implemented. Aborting test per security policy.")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def test_get_agents_skip_param_not_integer(api_base_url, auth_header):
    """
    Test Case ID: TC-GET-2f1c1c7e-007
    Description: Validate that GET /api/agents/ returns a 422 validation error when skip parameter is not an integer.
    Standards: RFC 8259, OWASP ASVS (V5,V10), ISO/IEC/IEEE 29148
    """
    endpoint = f"{api_base_url}/api/agents/"
    params = {"skip": "abc"}

    # Step 1: Send GET request with invalid skip
    response = requests.get(endpoint, headers=auth_header, params=params)

    # Expected Result 1: Status 422 per OpenAPI + RFC8259 compliance
    assert response.status_code == 422, f"Expected status code 422, got {response.status_code}"

    # Expected Result 2: Response body contains validation error details per schema
    try:
        resp_json = response.json()
    except Exception as e:
        pytest.fail(f"Response is not a valid JSON document (RFC8259): {e}")

    assert is_valid_validation_error(resp_json), (
        f"Response schema does not match expected validation error format. Got: {resp_json}"
    )