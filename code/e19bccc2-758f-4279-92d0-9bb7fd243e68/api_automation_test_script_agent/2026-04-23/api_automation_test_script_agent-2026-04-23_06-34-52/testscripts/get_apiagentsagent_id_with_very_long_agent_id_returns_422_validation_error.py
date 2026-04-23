import pytest
import requests

BASE_URL = "https://api.example.com"  # Update as needed or parameterize this.
LONG_AGENT_ID_LENGTH = 1025  # Exceeds typical RFC/validation boundaries. Adjust if API defines this.
\****************(scope="session")
def bearer_token():
    # Implement token retrieval via secure mechanism or parameterize via a secrets manager.
    # For compliance (OWASP ASVS V5, V10): never hardcode secrets.
    # Placeholder - replace with secure retrieval in production automation:
    import os
    token = os.environ.get('API_BEARER_TOKEN')
    if not token:
        pytest.fail("Bearer token not provided; set 'API_BEARER_TOKEN' env var.")
    return token
\****************(scope="function", autouse=True)
def check_api_reachable():
    health_url = f"{BASE_URL}/healthz"
    try:
        resp = requests.get(health_url, timeout=5)
        assert resp.status_code < 500, "API is not reachable."
    except Exception as e:
        pytest.fail(f"API is not reachable: {e}")
\*************.owasp_v5\*************.owasp_v10\************************\**********************\************************\*************.risk_level_medium\*************.testcase_id('TC-GET-2e2e0c6c-007')
def test_get_agent_with_excessively_long_id(bearer_token):
    """
    Validate that a GET request to /api/agents/{agent_id} with an excessively long agent_id returns HTTP 422 with validation error details.
    Traces to: OWASP ASVS V5 (Validation), V10 (API Security), RFC 8259, ISO/IEC/IEEE 29148
    """
    # Step 1: Compose an excessively long agent_id
    very_long_agent_id = 'A' * LONG_AGENT_ID_LENGTH
    endpoint = f"{BASE_URL}/api/agents/{very_long_agent_id}"
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Accept": "application/json"
    }
    # Step 2: Send GET request
    response = requests.get(endpoint, headers=headers, timeout=10)
    # Step 3: Validate response code (ISO/IEC/IEEE 29148: traceable requirement)
    assert response.status_code == 422, f"Expected 422, got {response.status_code}. Response: {response.text}"
    # Step 4: Validate JSON structure (RFC 8259 compliance)
    try:
        data = response.json()
    except Exception as exc:
        pytest.fail(f"Response is not valid JSON (RFC8259): {exc}. Raw response: {response.text}")
    # Step 5: Validate error field and schema
    assert "detail" in data, "Response body missing required 'detail' field as per OpenAPI spec, RFC 8259, and ASVS."
    assert isinstance(data["detail"], list), "'detail' field must be an array of error descriptors."
    # Validate each error object for required fields/structure
    for err in data["detail"]:
        assert isinstance(err, dict), "Each detail entry should be a JSON object."
        assert "loc" in err and isinstance(err["loc"], list), "Each error must include 'loc' as list per schema."
        assert "msg" in err and isinstance(err["msg"], str), "Each error must include 'msg' as string."
        assert "type" in err and isinstance(err["type"], str), "Each error must include 'type' as string."

