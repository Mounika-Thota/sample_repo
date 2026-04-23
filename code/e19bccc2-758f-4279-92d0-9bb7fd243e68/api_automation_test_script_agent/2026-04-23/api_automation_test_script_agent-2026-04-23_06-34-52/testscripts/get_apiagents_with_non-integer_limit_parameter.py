import pytest
import requests

# Configuration for RFC 8259, OWASP ASVS, ISO/IEC/IEEE 29148 compliance
API_BASE_URL = "<REPLACE_WITH_API_BASE_URL>"  # RFC 8259-compliant URL
AUTH_TOKEN = "<REPLACE_WITH_TOKEN>"
\****************(scope="module")
def api_headers():
    """Fixture: Returns common headers for authenticated requests (OWASP ASVS V5, V10)"""
    return {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
\****************(scope="module")
def api_reachable():
    """
    Precondition: API is reachable and responds to health check (ISO/IEC/IEEE 29148, OWASP ASVS V5)
    """
    health_check_url = f"{API_BASE_URL}/health"
    resp = requests.get(health_check_url)
    assert resp.status_code == 200, "API is not reachable (health check failed)"
    return True
\**********************\************************\******************("V5", "V10")
def test_get_agents_limit_not_integer(api_reachable, api_headers):
    """
    TC-GET-2f1c1c7e-008: Validate that GET /api/agents/ returns a 422 validation error
    when limit parameter is not an integer.
    
    Compliance references:
    - RFC 8259: strict JSON parsing/structure
    - OWASP ASVS V5, V10: authentication, input validation
    - ISO/IEC/IEEE 29148: requirements traceability & verifiability
    """
    params = {
        "limit": "xyz"  # Should trigger validation error
    }
    response = requests.get(f"{API_BASE_URL}/api/agents/", headers=api_headers, params=params)
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
    try:
        resp_json = response.json()
    except Exception as e:
        pytest.fail(f"Response body is not valid JSON (RFC 8259): {e}")

    # Expected schema: {'detail': [{'loc': [...], 'msg': 'string', 'type': 'string'}]}
    assert "detail" in resp_json, "Response missing 'detail' key (OWASP ASVS V10)"
    assert isinstance(resp_json["detail"], list), "'detail' is not a list (RFC 8259)"
    for error_detail in resp_json["detail"]:
        # Must have: loc, msg, type
        assert isinstance(error_detail, dict), "Error detail is not object (RFC 8259)"
        for field in ["loc", "msg", "type"]:
            assert field in error_detail, f"Missing '{field}' in validation error (ISO/IEC/IEEE 29148)"
        assert isinstance(error_detail["msg"], str), "'msg' should be a string"
        assert isinstance(error_detail["type"], str), "'type' should be a string"

    # ISO/IEC/IEEE 29148: Traceability
    # Requirement ID: TC-GET-2f1c1c7e-008 | Source: openapi_spec | Risk level: medium
    # All validations performed are traceable and verifiable per standards.

# No teardown required as no persistent changes are made