import pytest
import requests
\****************(scope="module")
def api_base_url():
    # Replace with your actual API base URL, parameterize for maintainability
    return "https://api.example.com"  # ISO 29148: Use clear, parameterized sources
\****************(scope="module")
def valid_bearer_token():
    # Fetch or inject a valid Bearer token (do not hardcode)
    # For compliance, trace token acquisition in your test infra, not here
    # E.g.: os.environ["BEARER_TOKEN"]
    return "<REPLACE_WITH_TOKEN>"
\****************(scope="function")
def setup_headers(valid_bearer_token):
    return {
        "Authorization": f"Bearer {valid_bearer_token}",
        "Content-Type": "application/json"
    }
\************************\********************\*************.owasp_asvs("V5")\*************.high_risk\********************("openapi_spec", id="create_agent_api_agents__post")
def test_post_agent_invalid_category(api_base_url, setup_headers):
    """
    TC-POST-9a0eda3c-005
    Verify API rejects payload with invalid category value not in enumeration list.
    Standards: ISO/IEC/IEEE 29148 (requirements trace), RFC 8259 (JSON), OWASP ASVS (V5)
    Preconditions:
      - API is reachable
      - Valid Bearer token is available
    Steps:
      1. Send POST request to /api/agents/ with non-empty slug, non-empty display_name, invalid category value.
    Expected results:
      - Status 422 returned
      - Error message indicates invalid enum value for category
    """
    payload = {
        "slug": "agent-invalid-cat",   # ISO/IEC/IEEE 29148: Clear requirement for slug, non-empty
        "display_name": "Invalid Cat Agent",  # Same: clear, traceable
        "category": "invalid_category"   # Constraint: must NOT match enum
    }
    endpoint = f"{api_base_url}/api/agents/"
    response = requests.post(endpoint, json=payload, headers=setup_headers)

    # Alignment with RFC 8259: validate response as valid JSON
    try:
        resp_json = response.json()
    except Exception as e:
        pytest.fail(f"Response is not valid JSON (RFC 8259 compliance): {e}")

    # Requirement: Status 422
    assert response.status_code == 422, f"Expected status 422, got {response.status_code}"

    # Requirement: Error message schema (OWASP ASVS: error clarity)
    assert "detail" in resp_json, "Response missing 'detail' property (ISO 29148 trace: error reporting)"
    detail_list = resp_json["detail"]
    # RFC 8259: details should be array, not null
    assert isinstance(detail_list, list), "'detail' is not a list (RFC 8259 compliance)"

    category_error = None
    for item in detail_list:
        if item.get("loc") == ["body", "category"]:
            if item.get("msg") == "value is not a valid enumeration member" and item.get("type") == "type_error.enum":
                category_error = item
                break
    assert category_error is not None, (
        "Error message for invalid 'category' not found or does not match expected schema. "
        "Got details: %s" % detail_list
    )

    # For traceability (ISO 29148): Log test ID and standards reference
    print("TC-POST-9a0eda3c-005 PASS : ISO/IEC/IEEE 29148, RFC 8259, OWASP ASVS V5")
