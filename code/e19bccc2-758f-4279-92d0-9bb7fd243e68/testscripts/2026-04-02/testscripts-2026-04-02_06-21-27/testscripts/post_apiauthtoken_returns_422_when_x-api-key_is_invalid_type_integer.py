import pytest
import requests

BASE_URL = "http://localhost"  # Replace with actual API base URL if different
ENDPOINT = "/api/auth/token"
\****************(scope="module")
def api_url():
    """
    Fixture to provide the full API endpoint URL.
    """
    return f"{BASE_URL}{ENDPOINT}"
\****************(scope="module")
def session():
    """
    Fixture to provide a requests session for connection pooling.
    """
    with requests.Session() as s:
        yield s

def test_post_token_with_integer_api_key(api_url, session):
    """
    Validate that the /api/auth/token endpoint returns a 422 status and a validation error
    when x-api-key header is provided as an integer instead of a string.
    
    Compliance:
      - ISO/IEC/IEEE 29148: Requirements traceability and verifiability
      - RFC 8259: JSON response validation
      - OWASP ASVS (V2, V5, V10): Input validation and error handling
    """
    # Step: Send POST request to /api/auth/token with x-api-key header set to an integer value
    headers = {
        "x-api-key": 123456,  # Intentionally incorrect type
        "Content-Type": "application/json"
    }
    response = session.post(api_url, headers=headers)

    # Assert: Status 422
    assert response.status_code == 422, (
        f"Expected status code 422, got {response.status_code}. "
        f"Response: {response.text}"
    )

    # Assert: Content-Type header is application/json (RFC 8259)
    content_type = response.headers.get("Content-Type", "")
    assert content_type.startswith("application/json"), (
        f"Expected 'Content-Type' to be 'application/json', got '{content_type}'"
    )

    # Assert: Response body contains 'detail' field with validation error information
    try:
        resp_json = response.json()
    except Exception as e:
        pytest.fail(f"Response body is not valid JSON: {e}\nRaw response: {response.text}")

    assert "detail" in resp_json, (
        "Response JSON does not contain 'detail' field as required by RFC 8259 and OWASP ASVS."
    )
    
    # Assert: 'detail' is a list of validation errors
    detail = resp_json["detail"]
    assert isinstance(detail, list), (
        f"'detail' field is not a list. Got: {type(detail)}"
    )
    
    # Each error in detail should have 'loc', 'msg', 'type' fields (ISO/IEC/IEEE 29148 traceability)
    for error in detail:
        assert isinstance(error, dict), f"Each error in 'detail' must be a dict. Got: {type(error)}"
        for field in ["loc", "msg", "type"]:
            assert field in error, f"Validation error does not contain '{field}' field. Error: {error}"
        assert isinstance(error["loc"], list), f"'loc' field must be a list. Got: {type(error['loc'])}"
        assert isinstance(error["msg"], str), f"'msg' field must be a string. Got: {type(error['msg'])}"
        assert isinstance(error["type"], str), f"'type' field must be a string. Got: {type(error['type'])}"

    # Traceability: Link to OWASP ASVS V2, V5, V10
    # - V2: Authentication
    # - V5: Validation, Sanitization and Encoding
    # - V10: Error Handling and Logging
    # These are covered by the validation of error response and status code.
