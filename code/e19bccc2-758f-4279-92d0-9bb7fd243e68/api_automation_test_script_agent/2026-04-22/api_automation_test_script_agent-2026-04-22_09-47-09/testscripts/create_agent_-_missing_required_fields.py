import pytest
import requests

API_BASE_URL = "https://your-api-host.com"  # Replace with actual API host
ENDPOINT = "/api/agents/"

@pytest.fixture(scope="module")
def bearer_token():
    # Setup for token retrieval
    # Replace this with a secure token retrieval mechanism
    token = "<REPLACE_WITH_TOKEN>"  # Ensure token is dynamically loaded for compliance
    assert token.startswith("eyJ"), "Token appears invalid or missing (OWASP ASVS V5, V10)"
    yield token
    # Teardown - nothing required as token is ephemeral

@pytest.mark.parametrize("missing_field, request_body, expected_loc", [
    ("slug",      {"display_name": "Agent Name", "category": "default"}, ["body", "slug"]),
    ("display_name", {"slug": "agent-001", "category": "default"}, ["body", "display_name"]),
    ("category",  {"slug": "agent-001", "display_name": "Agent Name"}, ["body", "category"]),
])
def test_post_agents_validation_missing_fields(bearer_token, missing_field, request_body, expected_loc):
    """
    TC-POST-7dead6b2-001
    Validate POST /api/agents/ fails with 422 when required fields are missing.

    Standards: RFC 8259 (JSON), OWASP ASVS V5, V10 (Input Validation), ISO/IEC/IEEE 29148 (Traceability)
    """
    url = f"{API_BASE_URL}{ENDPOINT}"
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json=request_body)

    # RFC 8259: Ensure response is well-formed JSON
    try:
        resp_json = response.json()
    except Exception as ex:
        pytest.fail(f"Response is not valid JSON: {ex}")

    # ISO/IEC/IEEE 29148 Requirement Trace: TC-POST-7dead6b2-001
    assert response.status_code == 422, (
        f"Expected status code 422 per spec (OWASP ASVS V5), got {response.status_code}"  
    )

    # OWASP ASVS V10: Detailed validation error in response
    assert "detail" in resp_json, "Missing 'detail' field in response body as per API spec and ASVS"
    assert isinstance(resp_json["detail"], list), "'detail' field should be a list of ValidationError objects"
    err_fields = [err for err in resp_json["detail"] if err.get("loc") == expected_loc]
    assert err_fields, (
        f"Validation error for missing field '{missing_field}' not found in response (ASVS trace)"
    )
    for err in err_fields:
        # RFC8259: Strings for 'msg', 'type' per schema
        assert isinstance(err.get("msg"), str), "'msg' should be a string per response schema (RFC 8259)"
        assert isinstance(err.get("type"), str), "'type' should be a string per response schema (RFC 8259)"
        assert "missing" in err.get("msg", "").lower(), (
            f"Error message should indicate missing field: {err.get('msg')} (ASVS V10)"
        )

    # ISO/IEC/IEEE 29148: Each requirement is verifiable and referenced
    # OWASP ASVS - Confirm no information leak in error response
    assert not any("traceback" in (err.get("msg") or "") for err in resp_json["detail"]), (
        "Response should not include stack traces or sensitive info (ASVS V10)"
    )