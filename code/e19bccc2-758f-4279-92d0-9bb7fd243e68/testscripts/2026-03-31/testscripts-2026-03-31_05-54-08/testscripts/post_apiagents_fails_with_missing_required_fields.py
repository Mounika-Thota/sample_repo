import pytest
import requests

BASE_URL = "https://api.example.com"  # Replace with actual API base URL
API_ENDPOINT = "/api/agents/"
\****************(scope="module")
def bearer_token():
    """
    Fixture to provide a valid Bearer token.
    Replace with secure retrieval mechanism as per ISO/IEC/IEEE 29148 traceability and OWASP ASVS authentication requirements.
    """
    # Example: token = get_token_from_secure_store()
    token = "<REPLACE_WITH_TOKEN>"
    assert token and token != "<REPLACE_WITH_TOKEN>", "Bearer token must be set for compliance."
    return token
\****************(scope="module")
def api_url():
    """
    Fixture to provide the complete API URL.
    """
    return f"{BASE_URL}{API_ENDPOINT}"
\************************\********************\*************.owasp_asvs(["V5", "V10"])
def test_post_agents_missing_required_fields(api_url, bearer_token):
    """
    TC-POST-0d8b8c2f-002
    Verify that omitting required fields (slug, display_name, category) returns 422 with validation error.
    Standards: ISO/IEC/IEEE 29148 (requirements traceability), RFC 8259 (JSON compliance), OWASP ASVS (input validation).
    """
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    # Body intentionally missing required fields per test case
    payload = {}  # RFC 8259 compliant empty JSON object

    response = requests.post(api_url, headers=headers, json=payload)

    # Assert status code
    assert response.status_code == 422, (
        f"Expected HTTP 422 for missing required fields, got {response.status_code}. "
        "(OWASP ASVS V5: Input Validation, ISO/IEC/IEEE 29148: Requirement TC-POST-0d8b8c2f-002)"
    )

    # Assert response body structure
    try:
        resp_json = response.json()
    except ValueError:
        pytest.fail("Response is not valid RFC 8259 JSON.")

    assert "detail" in resp_json, (
        "Response must contain 'detail' array per OpenAPI spec and ISO/IEC/IEEE 29148 traceability."
    )
    assert isinstance(resp_json["detail"], list), (
        "'detail' must be an array (RFC 8259 compliance)."
    )

    # Validate that each required field is mentioned in the validation errors
    missing_fields = {"slug", "display_name", "category"}
    found_fields = set()
    for error in resp_json["detail"]:
        loc = error.get("loc", [])
        if len(loc) > 0 and isinstance(loc[0], str):
            field = loc[0]
            if field in missing_fields:
                found_fields.add(field)
        assert "msg" in error and isinstance(error["msg"], str), (
            "Each error must have a 'msg' string (ISO/IEC/IEEE 29148, RFC 8259)."
        )
        assert "type" in error and isinstance(error["type"], str), (
            "Each error must have a 'type' string (OpenAPI spec compliance)."
        )

    assert missing_fields.issubset(found_fields), (
        f"Validation errors must reference all missing fields: {missing_fields} (OWASP ASVS V10: Error Handling)."
    )

    # Traceability: Ensure test case ID and standards are referenced
    # (ISO/IEC/IEEE 29148: Requirement traceability, OWASP ASVS: Input validation, RFC 8259: JSON compliance)

# No teardown required as no data is created.