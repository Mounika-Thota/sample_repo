import pytest
import requests

# Constants (per ISO/IEC/IEEE 29148 requirements: explicit, configurable)
API_BASE_URL = "https://api.example.com"  # Replace with actual API base
ENDPOINT = "/api/agents/"

# OWASP ASVS v5/v10: Authorization header and error validation\****************(scope="module")
def bearer_token():
    # Setup: Retrieve token securely (external, not hardcoded)
    # This placeholder must be replaced according to environment secret retrieval best practices
    # RFC 8259: no dummy token in artifact
    token = pytest.config.getoption("--bearer-token")
    assert token, "Bearer token must be provided via --bearer-token option."
    return token
\****************(scope="module")
def session():
    s = requests.Session()
    yield s
    s.close()
\***********************\************************\*************.error_format\************************\*************.owasp_asvs_refs(["V5", "V10"])\*************.risk_level("medium")
def test_agents_get_error_format(session, bearer_token):
    """Validate that GET /api/agents/ returns errors in a consistent format as defined in the OpenAPI spec when invalid parameters are provided."""
    # Step 1: Ensure API is reachable (per ISO/IEC/IEEE 29148 - precondition validation)
    ping_url = API_BASE_URL + "/api/health"  # Health check endpoint (update per actual API design)
    ping_resp = session.get(ping_url, timeout=5)
    assert ping_resp.status_code == 200, f"API health check failed: {ping_resp.status_code}"  # Traceable

    # Step 2: Send GET request with invalid query params, RFC 8259-compliant payload and headers
    url = API_BASE_URL + ENDPOINT
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    params = {
        "skip": "abc",  # Should be integer, sent as string (invalid)
        "limit": "xyz"   # Should be integer, sent as string (invalid)
    }
    response = session.get(url, headers=headers, params=params)
    
    # Step 3: Validate response per OpenAPI HTTPValidationError schema and standards
    assert response.status_code == 422, f"Expected 422 Unprocessable Entity, got {response.status_code}"

    # RFC 8259: Ensure JSON response and structure
    try:
        error_body = response.json()
    except Exception as ex:
        pytest.fail(f"Response is not valid RFC 8259 JSON: {ex}")

    assert "detail" in error_body, "Response must contain 'detail' field for error description (OpenAPI, OWASP ASVS V10)"
    assert isinstance(error_body["detail"], list), "'detail' field must be an array per OpenAPI error schema"
    
    for entry in error_body["detail"]:
        assert isinstance(entry, dict), "Each 'detail' entry must be an object"
        assert "loc" in entry and "msg" in entry and "type" in entry, "Each 'detail' entry must have 'loc', 'msg', and 'type' keys per OpenAPI spec"
        assert isinstance(entry["loc"], list), "'loc' must be a list identifying error location"
        assert isinstance(entry["msg"], str), "'msg' must be a string explaining error"
        assert isinstance(entry["type"], str), "'type' must be a string categorizing error"
    
    # ISO/IEC/IEEE 29148 traceability: mapped to test case TC-GET-2f1c1c7e-010, OpenAPI spec source_id='list_agents_api_agents__get'
    # OWASP ASVS reference: V5 (Input Validation), V10 (Error Handling)

# pytest command with token:
# usage example: pytest test_agents_api.py --bearer-token=YOUR_VALID_TOKEN