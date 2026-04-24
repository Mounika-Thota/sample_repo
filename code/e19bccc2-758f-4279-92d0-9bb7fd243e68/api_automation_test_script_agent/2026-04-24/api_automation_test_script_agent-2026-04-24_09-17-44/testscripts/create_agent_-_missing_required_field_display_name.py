import pytest
import requests

# -- STANDARDS AND COMPLIANCE TRACEABILITY --
# 1. RFC 8259: Ensures all request/response bodies are JSON compliant.
# 2. OWASP ASVS V5, V10: Ensures validation of server-side input validation and error handling.
# 3. ISO/IEC/IEEE 29148: Provides requirements traceability back to testcase ID TC-POST-7f2b9c6b-003.

API_BASE_URL = "<REPLACE_WITH_BASE_URL>"  # Assign actual API base URL in environment or CI config
API_ENDPOINT = "/api/agents/"
BEARER_TOKEN = "<REPLACE_WITH_TOKEN>"      # Use fixture or secure environment variable in CI
\****************(scope="module", autouse=True)
def check_api_reachable():
    """
    Precondition: Ensure the API base URL is reachable before running tests.
    Compliance: ISO/IEC/IEEE 29148 (preconditions verified)
    """
    health_url = API_BASE_URL + "/health"  # Adjust health endpoint as needed
    try:
        resp = requests.get(health_url, timeout=5)
        assert resp.status_code < 500, f"API not reachable: {resp.status_code} {resp.text}"
    except Exception as ex:
        pytest.skip(f"Cannot reach required API endpoint: {ex}")
\****************
def valid_headers():
    """
    Returns required headers, enforcing RFC 8259 content type declaration.
    """
    return {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
\************************\********************\**********************\*************.owasp_asvs(["V5", "V10"])
def test_create_agent_missing_display_name(valid_headers):
    """
    TestCase ID: TC-POST-7f2b9c6b-003
    Requirement: Validate error response when display_name is missing from request body.
    Standards Trace: RFC 8259, OWASP ASVS V5/V10, ISO/IEC/IEEE 29148
    Steps:
      - Send POST request to /api/agents/ with slug and category, omitting display_name.
      - Expect status 422 and error detail for missing display_name.
    """
    # Prepare minimal, standards-compliant JSON body (RFC 8259)
    request_body = {
        "slug": "agent-003",  # Should be unique in actual use; here as example
        "category": "api_doc_testing"
        # "display_name" intentionally omitted
    }
    url = API_BASE_URL + API_ENDPOINT
    response = requests.post(url, json=request_body, headers=valid_headers)

    # Assert correct status code is returned (ISO/IEC/IEEE 29148, OWASP ASVS)
    assert response.status_code == 422, f"Expected 422, got {response.status_code}: {response.text}"

    # Assert response body is RFC 8259-compliant JSON
    try:
        resp_json = response.json()
    except Exception as exc:
        pytest.fail(f"Response is not valid RFC 8259 JSON: {exc}\nBody: {response.text}")

    # Schema: {"detail": [ {"loc": [...], "msg": ..., "type": ...} ]}
    assert "detail" in resp_json, "Response must include 'detail' key in body"
    details = resp_json["detail"]
    assert isinstance(details, list), "'detail' should be a list (validation errors)"
    
    # Each entry must have 'loc', 'msg', and 'type'; locate 'display_name' error
    missing_display_name_error = False
    for error in details:
        assert all(k in error for k in ("loc", "msg", "type")), \
            f"Error object missing required fields: {error}"
        # Typical Pydantic/FastAPI loc is tuple/list, e.g. ("body", "display_name")
        if any("display_name" in str(loc_part) for loc_part in error["loc"]):
            # OWASP ASVS: Ensure message indicates missing/required field
            if "required" in error["msg"].lower() or "missing" in error["msg"].lower():
                missing_display_name_error = True
                break
    assert missing_display_name_error, "No validation error found for missing 'display_name' field"
