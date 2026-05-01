import pytest
import requests

API_BASE_URL = "https://api.example.com"  # Replace with actual API base URL
ENDPOINT = "/api/agents/"
\****************(scope="module")
def bearer_token():
    # Ideally, obtain a token securely (not hardcoded), e.g. via OAuth/Login API
    # Example: return get_token_from_secure_source()
    return "<REPLACE_WITH_TOKEN>"  # Replace with valid token as per test setup
\****************(scope="module")
def session():
    s = requests.Session()
    yield s
    s.close()
\************************\**********************\******************("V5", "V10")
def test_post_agents_missing_display_name(session, bearer_token):
    """
    TC-POST-9a0eda3c-003
    ISO/IEC/IEEE 29148 Trace: Requirement - API input validation (mandatory fields), Error handling compliance.
    RFC 8259: JSON payloads, JSON error response verification.
    OWASP ASVS: V5 (Validation), V10 (Error Handling).
    Preconditions: API is reachable, valid Bearer token.
    Step: Send POST request to /api/agents/ with slug and category, omitting display_name.
    Expected: Status 422, response body indicates missing 'display_name' field
    """
    url = f"{API_BASE_URL}{ENDPOINT}"
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    # Construct payload: EXCLUDE display_name intentionally
    payload = {
        "slug": "test-agent",           # 'slug' present, non-empty
        "category": "testing"           # 'category' present, valid enum
    }
    # Send POST request
    response = session.post(url, headers=headers, json=payload)

    # RFC 8259: Ensure JSON response body
    try:
        resp_json = response.json()
    except ValueError:
        pytest.fail("Response is not valid JSON (RFC 8259 compliance)")

    # ISO/IEC/IEEE 29148: Requirements trace
    # Validate: Status
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    # Validate response body structure and error for missing 'display_name'
    assert "detail" in resp_json, "'detail' field missing in response body"
    detail_list = resp_json["detail"]
    # Each item in detail should be a dict with loc/msg/type
    # At least one error must reference body/display_name with type 'value_error.missing'
    error_found = False
    for err in detail_list:
        if err.get("loc") == ["body", "display_name"] and \
           err.get("msg") == "field required" and \
           err.get("type") == "value_error.missing":
            error_found = True
            break
    assert error_found, "Missing required field error for 'display_name' not found in response body"

    # ASVS V5: Ensure precise input validation and error typing (no generic errors)
    # ASVS V10: No information disclosure in error (check error contents)
    # (Additional checks can be hooked as needed.)
