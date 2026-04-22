import pytest
import requests

# --- Configuration and Standard Compliance Annotations ---
# Standards: RFC 8259 (JSON syntax), OWASP ASVS (V5: Input Validation), ISO/IEC/IEEE 29148 (Requirements traceability)
# Test Case: TC-DELETE-f2e6c865-004
# Source: OpenAPI Spec (delete_agent_api_agents__agent_id__delete)
# Tags: regression, input-validation
# Risk Level: Medium

def get_valid_bearer_token():
    # Placeholder for actual token retrieval logic
    # This should fetch a valid Bearer token as per security/auth configuration
    raise NotImplementedError("Implement token retrieval mechanism per environment setup.")

@pytest.fixture(scope="session")
def api_base_url():
    # Replace with your actual API base URL
    return "https://api.example.com"

@pytest.fixture(scope="session")
def bearer_token():
    # Securely fetch and provide a valid Bearer token
    return get_valid_bearer_token()

@pytest.mark.regression
@pytest.mark.input_validation
@pytest.mark.owasp_asvs('V5')
def test_delete_agent_missing_agent_id(api_base_url, bearer_token):
    """
    TC-DELETE-f2e6c865-004
    Verify that the endpoint returns 422 when the agent_id path parameter is missing.
    Standards: RFC 8259 (JSON), OWASP ASVS (V5: Input Validation), ISO/IEC/IEEE 29148
    """
    endpoint = f"{api_base_url}/api/agents/"  # agent_id is intentionally omitted
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }

    # Step 1: Preconditions checked via fixtures
    # Step 2: Send DELETE request without required path parameter
    response = requests.delete(endpoint, headers=headers)

    # Validation 1: Status 422
    assert response.status_code == 422, (
        f"Expected status code 422, got {response.status_code}. "
        f"Response body: {response.text}"
    )

    # Validation 2: RFC 8259 compliance (response must be valid JSON)
    try:
        resp_json = response.json()
    except ValueError as e:
        pytest.fail(f"Response is not valid RFC 8259 JSON: {e}\nResponse body: {response.text}")
    
    # Validation 3: Schema and error structure per OpenAPI and ASVS
    # Validate 'detail' as a list containing at least one error
    assert 'detail' in resp_json, "Response JSON must contain top-level 'detail' key as per schema."
    assert isinstance(resp_json['detail'], list), "'detail' value must be a list."
    assert len(resp_json['detail']) > 0, "'detail' list must not be empty."
    for error in resp_json['detail']:
        # Check required keys and types per schema
        assert isinstance(error, dict), "Each detail entry must be a JSON object."
        assert 'loc' in error and isinstance(error['loc'], list), "Each error must have a 'loc' list."
        assert all(isinstance(loc, (str, int)) for loc in error['loc']), "Each 'loc' entry must be string or integer."
        assert 'msg' in error and isinstance(error['msg'], str), "Each error must have 'msg' string."
        assert 'type' in error and isinstance(error['type'], str), "Each error must have 'type' string."

    # ISO/IEC/IEEE 29148 Traceability:
    # - Requirement: Endpoint enforces validation for missing required path parameters
    # - Test: When agent_id is omitted, returns 422 and validation details

# No teardown is required as the operation is negative and does not modify API state.
