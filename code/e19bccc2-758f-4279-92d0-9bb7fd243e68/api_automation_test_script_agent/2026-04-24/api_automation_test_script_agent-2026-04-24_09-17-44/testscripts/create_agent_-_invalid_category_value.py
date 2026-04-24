import pytest
import requests

BASE_URL = "https://api.example.com"  # Replace with actual API base URL if known
def get_valid_bearer_token():
    """Stub: Replace with actual authentication logic or fixture."""
    # Example: return obtain_token_from_identity_provider()
    return "<REPLACE_WITH_TOKEN>"
\****************(scope="module")
def auth_header():
    token = get_valid_bearer_token()
    assert token and token != "<REPLACE_WITH_TOKEN>", "Bearer token must be set and not a placeholder."
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
\************************\********************\*************.owasp_asvs(["V5", "V10"])
def test_post_agent_invalid_category(auth_header):
    """
    TC-POST-7f2b9c6b-005: Validate error response when category is not one of the allowed enum values.
    Standards: RFC 8259, OWASP ASVS (V5, V10), ISO/IEC/IEEE 29148
    Requirements are traceable via testcase id and OWASP ASVS refs.
    """
    url = f"{BASE_URL}/api/agents/"
    payload = {
        "slug": "agent-005",  # Should be unique per test run; consider dynamic generation if needed
        "display_name": "Agent Five",
        "category": "invalid_category"  # Intentionally invalid value; must NOT be in enum
    }

    response = requests.post(url, headers=auth_header, json=payload)

    # RFC 8259: Validate response is proper JSON
    try:
        resp_json = response.json()
    except Exception as exc:
        pytest.fail(f"Response is not valid JSON per RFC 8259: {exc}")

    # ISO/IEC/IEEE 29148: Requirements verification - traceability via testcase id
    assert response.status_code == 422, "Expected HTTP 422 Unprocessable Entity per schema and test requirement"

    # OWASP ASVS V5/V10: Error details must not expose sensitive info, must provide clear validation feedback
    assert "detail" in resp_json, "Response must contain 'detail' explaining validation error (OWASP ASVS V10)"
    assert isinstance(resp_json["detail"], list), "'detail' should be a list (per expected schema)"

    category_error_found = False
    for err in resp_json["detail"]:
        # ISO/IEC/IEEE: Verification of structure
        assert isinstance(err, dict), "Each 'detail' item must be an object"
        assert "loc" in err and "msg" in err and "type" in err, "Each error must contain 'loc', 'msg', and 'type'"
        # OWASP ASVS: Feedback must clearly indicate field and error type
        if "category" in err["loc"]:
            category_error_found = True
            assert "not a valid enum value" in err["msg"].lower() or "invalid value" in err["msg"].lower(), \
                "Error message must indicate invalid enum constraint"
    assert category_error_found, "Error detail must reference 'category' field per requirement."
