import pytest
import requests

def get_bearer_token():
    """
    Placeholder for obtaining a valid Bearer token.
    Should be implemented with actual authentication logic according to the system under test,
    and token should comply with RFC 8259 for JSON-based structures where relevant.
    """
    # Example: return os.environ["API_BEARER_TOKEN"]
    raise NotImplementedError("Bearer token retrieval must be implemented to ensure test traceability and reproducibility.")
\****************(scope="module")
def api_base_url():
    """
    Provide base API URL for maintainable endpoint referencing.
    """
    return "https://api.example.com"  # Replace with actual base URL as per test environment.
\****************(scope="function")
def bearer_token():
    """
    Retrieve a valid Bearer token before each test as per authentication requirements.
    """
    return get_bearer_token()

def test_get_agents_missing_agent_id(api_base_url, bearer_token):
    """
    TC-GET-2e2e0c6c-005:
    Validate that a GET request to /api/agents/{agent_id} without providing agent_id returns HTTP 422 with validation error details.
    Compliance:
      - RFC 8259: Ensures JSON payload in error response is standard-compliant.
      - OWASP ASVS V5, V10: Ensures robust input validation and secure error reporting.
      - ISO/IEC/IEEE 29148: Requirements are traceable and verifiable via assertion and coverage mapping.
    """
    endpoint = f"{api_base_url}/api/agents/"  # agent_id intentionally omitted
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Accept": "application/json"
    }
    response = requests.get(endpoint, headers=headers)

    # Assert status code is 422 Unprocessable Entity
    assert response.status_code == 422, (
        f"Expected HTTP 422, got {response.status_code}. Compliance: RFC 8259, OWASP ASVS V5/V10."
    )

    # Assert response is valid RFC 8259-compliant JSON
    try:
        resp_data = response.json()
    except ValueError:
        pytest.fail("Response payload is not valid RFC 8259 JSON.")

    # Assert presence and correctness of the 'detail' field per OpenAPI schema, for verifiable validation feedback
    assert 'detail' in resp_data, (
        "Response missing 'detail' field required for validation error details (ISO/IEC/IEEE 29148 traceability, OWASP ASVS V5)."
    )
    detail = resp_data['detail']
    assert isinstance(detail, list), (
        "'detail' field is not a list, does not match schema for validation errors (RFC 8259 compliance)."
    )
    for error in detail:
        assert 'loc' in error and 'msg' in error and 'type' in error, (
            "Each item in 'detail' must have 'loc', 'msg', and 'type' fields (OpenAPI, ISO/IEC/IEEE 29148 compliance)."
        )
        assert isinstance(error['loc'], list), "'loc' field must be a list."
        assert isinstance(error['msg'], str), "'msg' field must be a string."
        assert isinstance(error['type'], str), "'type' field must be a string."
    # Requirements traceable to: OWASP ASVS V5/V10, RFC 8259, ISO/IEC/IEEE 29148

# To run:
# pytest test_get_agents_negative.py