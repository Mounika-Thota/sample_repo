import os
import pytest
import requests

def get_bearer_token():
    """
    Retrieves a valid bearer token from environment or a secure source.
    Implementation must guarantee token confidentiality in alignment with OWASP ASVS V5.
    """
    token = os.getenv("BEARER_TOKEN")
    if not token:
        raise EnvironmentError("BEARER_TOKEN not set in environment.")
    return token

@pytest.fixture(scope="module")
def api_base_url():
    # Base URL should be defined as a parameter or environment variable per ISO/IEC/IEEE 29148 traceability
    base_url = os.getenv("API_BASE_URL")
    if not base_url:
        raise EnvironmentError("API_BASE_URL not set in environment.")
    return base_url.rstrip("/")

@pytest.fixture
def auth_header():
    token = get_bearer_token()
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

def test_get_agents_skip_string_returns_422(api_base_url, auth_header):
    """
    Test Case: TC-GET-2e798b8e-02
    Description: Validate error response when skip query parameter is a string, violating schema.
    Compliance: RFC 8259 (JSON), OWASP ASVS (V5, V10), ISO/IEC/IEEE 29148
    Traceability: OpenAPI source_id=api-agents-get
    """
    endpoint = f"{api_base_url}/api/agents/"
    params = {
        'skip': 'invalid'  # Non-integer string to trigger validation error
    }

    # Step: Send GET request with invalid skip
    response = requests.get(endpoint, headers=auth_header, params=params, timeout=10)

    # Validation 1: Status code must be 422
    assert response.status_code == 422, f"Expected status 422, got {response.status_code}"

    # Validation 2: Response is valid JSON (per RFC 8259)
    try:
        resp_json = response.json()
    except Exception as e:
        pytest.fail(f"Response body not valid JSON: {e}")

    # Validation 3: Error response follows HTTPValidationError schema
    # Expected: {"detail": [{"loc": ["query", "skip"], "msg": "value is not a valid integer", "type": "type_error.integer"}]}
    assert 'detail' in resp_json, "'detail' field not present in error response"
    assert isinstance(resp_json['detail'], list), "'detail' field must be a list"
    found_skip_error = False
    for err in resp_json['detail']:
        if err.get('loc') == ['query', 'skip'] and \
           err.get('type') == 'type_error.integer' and \
           'not a valid integer' in err.get('msg', ''):
            found_skip_error = True
            break
    assert found_skip_error, (
        "Did not find expected validation error about 'skip' being a non-integer in response detail. "
        f"Actual detail: {resp_json['detail']}"
    )
    
    # Validation 4: Ensure no extra fields (minimal error info, per schema)
    allowed_error_fields = {"loc", "msg", "type"}
    for err in resp_json['detail']:
        assert set(err.keys()).issubset(allowed_error_fields), (
            f"Unexpected fields in error entry: {set(err.keys()) - allowed_error_fields}"
        )
