import pytest
import requests

BASE_URL = "http://localhost"  # Update to actual base URL if needed
API_ENDPOINT = "/api/agents/"
\****************(scope="module")
def auth_token():
    """
    Fixture for retrieving a valid bearer token.
    Token retrieval mechanism must be implemented as per project requirements (ISO/IEC/IEEE 29148: test data independence, RFC 8259 compatibility for JSON payloads).
    """
    # TODO: Integrate with actual token retrieval method or secure secrets
    return "<REPLACE_WITH_TOKEN>"
\****************(scope="module")
def ensure_existing_agent(auth_token):
    """
    Ensure the agent with slug 'agent-009' is present pre-test.
    Idempotent: will not fail if already exists (aligning with OWASP ASVS for predictable state).
    """
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "slug": "agent-009",
        "display_name": "Agent Nine",
        "category": "ui_automation"  # Assumes this is a valid enum
    }
    # Try to create; ignore conflicts as they mean the agent exists
    response = requests.post(BASE_URL + API_ENDPOINT, headers=headers, json=payload)
    if response.status_code not in (201, 409, 422):
        pytest.fail(f"Precondition setup failed. Unexpected response: {response.status_code} - {response.text}")
    yield
    # Teardown deliberately omitted: To preserve existing agent across regression runs; follows test independence (ISO/IEC/IEEE 29148)
\************************\**********************\*************.owasp_asvs(["V5", "V10"])
def test_duplicate_agent_slug_returns_error(auth_token, ensure_existing_agent):
    """
    TC-POST-7f2b9c6b-009: Validate error response when attempting to create
    an agent with a slug that already exists (RFC 8259, ISO/IEC/IEEE 29148, OWASP ASVS V5/V10)
    """
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "slug": "agent-009",
        "display_name": "Agent Nine",
        "category": "ui_automation"
    }
    response = requests.post(BASE_URL + API_ENDPOINT, headers=headers, json=payload)
    # RFC 8259: All JSON payloads used; expecting 422 Unprocessable Entity or 409 Conflict for duplicate slug
    assert response.status_code in [422, 409], (
        f"Expected status 422 or 409, got {response.status_code} ({response.text})"
    )
    resp_json = response.json()
    assert isinstance(resp_json, dict), "Response body must be a JSON object (RFC 8259)"
    assert "detail" in resp_json, (
        "Response must contain 'detail' key describing validation errors as per API schema."
    )
    detail = resp_json["detail"]
    assert isinstance(detail, list), "'detail' should be a list for validation errors (OpenAPI/ASVS log structure)"
    found_duplicate = False
    for err in detail:
        # ISO/IEC/IEEE 29148 trace: Each error object structure validation
        assert "loc" in err and "msg" in err and "type" in err, (
            "Each error in 'detail' must contain 'loc', 'msg', and 'type' per schema."
        )
        if (isinstance(err["loc"], list) and "slug" in err["loc"][0]) or "slug" in err.get("msg", "").lower():
            found_duplicate = True
            break
    assert found_duplicate, "A validation error for duplicate slug must be present."
