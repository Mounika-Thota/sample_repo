import pytest
import requests

def get_bearer_token():
    # Placeholder for obtaining a valid Bearer token.
    # In actual implementation, securely fetch from vault or env.
    # This function MUST be replaced/implemented per test infra.
    return "<REPLACE_WITH_TOKEN>"

@pytest.fixture(scope="module")
def api_base_url():
    # Base API URL SHOULD come from environment or configuration for portability (ISO/IEC/IEEE 29148)
    return "https://api.example.com"  # Replace with system-under-test URL

@pytest.fixture(scope="module")
def headers():
    # Authorization header with valid Bearer token
    token = get_bearer_token()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def test_post_agents_invalid_category(api_base_url, headers):
    """
    TC-POST-7dead6b2-002
    Validate POST /api/agents/ fails with 422 when 'category' contains a value not in the enum.

    Compliance: RFC 8259 (JSON encoding), OWASP ASVS (V5: Input validation, V10: Error handling), ISO/IEC/IEEE 29148 (requirements traceability)
    """
    endpoint = "/api/agents/"
    url = f"{api_base_url}{endpoint}"
    payload = {
        "category": "invalid_category"
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    # Assert status code is 422 (OWASP ASVS V5, V10)
    assert response.status_code == 422, f"Expected status 422, got {response.status_code}. Response: {response.text}"
    
    # Assert response conforms to expected error schema (RFC 8259, OWASP ASVS V10)
    try:
        resp_json = response.json()
    except ValueError as exc:
        pytest.fail(f"Response is not valid JSON (RFC 8259): {exc}\nRaw response: {response.text}")
    
    assert "detail" in resp_json, "Response must contain 'detail' key per error schema."
    assert isinstance(resp_json["detail"], list), "'detail' must be a list."
    
    error_found = False
    for error in resp_json["detail"]:
        # Each error must have 'loc', 'msg', 'type' keys per negative validation RFC and OpenAPI/ISO contract
        assert set(error).issuperset({"loc", "msg", "type"}), f"Error object missing keys: {error}"
        if ("category" in error.get("loc", []) and
            "enum" in error.get("type", "").lower()):
            error_found = True
            # Optionally, ensure error message mentions enum/invalid
            assert "invalid" in error["msg"].lower(), f"Error message should mention invalid value. Got: {error['msg']}"
    assert error_found, "ValidationError for invalid enum value in 'category' not found in response."

# END OF TEST CASE
