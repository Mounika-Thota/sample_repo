import pytest
import requests

def get_base_url():
    # Placeholder: Replace with actual base URL or use pytest config/fixture
    return "https://api.example.com"
\****************(scope="module")
def api_base_url():
    """
    Provides the base URL for the API under test.
    Traceability: ISO/IEC/IEEE 29148 (requirements traceability), RFC 8259 (JSON compliance)
    """
    return get_base_url()
\****************(scope="module")
def session():
    """
    Provides a requests session for connection pooling.
    """
    with requests.Session() as s:
        yield s

def test_post_auth_token_empty_api_key(api_base_url, session):
    """
    TC-POST-3d2e2f6b-003
    Validate that the /api/auth/token endpoint returns a 422 status and a validation error when x-api-key header is present but empty.
    
    Compliance:
      - ISO/IEC/IEEE 29148: Requirements traceability (test case ID, expected results)
      - RFC 8259: JSON response validation
      - OWASP ASVS: V2 (Authentication), V5 (Validation), V10 (Error Handling)
    """
    # Step 1: Send POST request with empty x-api-key header
    url = f"{api_base_url}/api/auth/token"
    headers = {
        "x-api-key": "",
        "Content-Type": "application/json"
    }
    response = session.post(url, headers=headers)

    # Assert 1: Status 422
    assert response.status_code == 422, f"Expected status 422, got {response.status_code}"

    # Assert 2: Content-Type header is application/json (RFC 8259)
    content_type = response.headers.get("Content-Type", "")
    assert content_type.startswith("application/json"), f"Expected Content-Type application/json, got {content_type}"

    # Assert 3: Response body contains 'detail' field with validation error information
    try:
        resp_json = response.json()
    except Exception as e:
        pytest.fail(f"Response is not valid JSON: {e}")
    assert "detail" in resp_json, "Response JSON must contain 'detail' field as per error schema (OWASP ASVS V10)"
    detail = resp_json["detail"]
    assert isinstance(detail, list), "'detail' field must be a list per schema"
    for err in detail:
        assert isinstance(err, dict), "Each error in 'detail' must be a dict"
        assert "loc" in err and isinstance(err["loc"], list), "Each error must have a 'loc' list (field location)"
        assert "msg" in err and isinstance(err["msg"], str), "Each error must have a 'msg' string (error message)"
        assert "type" in err and isinstance(err["type"], str), "Each error must have a 'type' string (error type)"

    # Traceability: Link test case ID, requirements, and standards in test docstring and assertions
