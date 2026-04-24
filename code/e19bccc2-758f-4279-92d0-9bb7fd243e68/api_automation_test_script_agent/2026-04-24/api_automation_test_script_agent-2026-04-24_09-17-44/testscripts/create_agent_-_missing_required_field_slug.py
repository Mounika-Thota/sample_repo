import pytest
import requests

API_BASE_URL = "https://api.example.com"  # TODO: Replace with actual API base URL
def get_valid_token():
    # This should implement acquiring/reading a valid bearer token in a secure, compliant way
    # Compliant with OWASP ASVS V5 (Identity & Authentication) and ISO/IEC/IEEE 29148 for requirements traceability
    # Example placeholder - replace with actual mechanism, e.g., vault integration/env var/config
    token = "<REPLACE_WITH_TOKEN>"  # Mandatory: Set securely and never hardcode in production
    assert token != "<REPLACE_WITH_TOKEN>", "Token must be securely provided."
    return token
\****************(scope="module")
def auth_headers():
    return {
        "Authorization": f"Bearer {get_valid_token()}",
        "Content-Type": "application/json"
    }
\****************(autouse=True)
def preconditions():
    # Ensure API is reachable before each test (ISO/IEC/IEEE 29148 – environmental precondition)
    health_endpoint = f"{API_BASE_URL}/health"  # Replace with appropriate health check endpoint
    try:
        r = requests.get(health_endpoint, timeout=5)
        assert r.status_code == 200, f"API health check failed: {r.status_code}"
    except Exception as ex:
        pytest.skip(f"Precondition failed: API not reachable: {ex}")
\*************.owasp_asvs(["V5", "V10"])\*************.risk_level("medium")\************************\********************\**************************("TC-POST-7f2b9c6b-002", source="openapi_spec:create_agent_api_agents__post")
def test_post_agent_missing_slug(auth_headers):
    """
    Validate error response when slug is missing from POST /api/agents/ request body.
    Standards: RFC 8259 (JSON), OWASP ASVS (V5, V10), ISO/IEC/IEEE 29148.
    """
    url = f"{API_BASE_URL}/api/agents/"
    payload = {
        "display_name": "Agent Two",
        "category": "usg"  # Presume 'usg' is a valid enum value per OpenAPI schema
    }
    response = requests.post(url, headers=auth_headers, json=payload)

    # 1. Status code is 422 (Unprocessable Entity), see RFC 8259, ISO/IEC/IEEE 29148 (ID: TC-POST-7f2b9c6b-002)
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    # 2. Response is valid RFC 8259-compliant JSON
    try:
        resp_json = response.json()
    except Exception:
        pytest.fail("Response body is not valid RFC 8259 JSON.")

    # 3. 'detail' field exists and matches expected error schema
    assert 'detail' in resp_json, "Missing 'detail' in error response."
    detail = resp_json['detail']
    assert isinstance(detail, list), "'detail' should be a list per OpenAPI schema."
    found_slug_error = False
    for error in detail:
        # Each error must comply with the schema {'loc': [string, integer], 'msg': string, 'type': string}
        assert isinstance(error, dict), "Each detail item should be object/json-dict."
        assert 'loc' in error, "Missing 'loc' in error detail."
        assert 'msg' in error, "Missing 'msg' in error detail."
        assert 'type' in error, "Missing 'type' in error detail."
        # Check for missing slug error (OWASP ASVS V10 – input/validation feedback)
        loc = error['loc']
        msg = error['msg']
        err_type = error['type']
        assert isinstance(loc, list), "'loc' should be a list."
        assert isinstance(msg, str), "'msg' should be a string."
        assert isinstance(err_type, str), "'type' should be a string."
        # Traceability: loc should mention 'slug' and msg/type indicate missing/required
        if any("slug" == seg for seg in loc) and ("missing" in msg.lower() or "required" in msg.lower()):
            found_slug_error = True
    assert found_slug_error, "No validation error found for the missing 'slug' field. (OWASP ASVS V10)"