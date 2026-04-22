import pytest
import requests

def get_bearer_token():
    # Implement a secure method to retrieve a valid token respecting RFC 8259 (proper JSON, no hardcoding)
    # Example: retrieve from environment variable or secure vault
    import os
    token = os.environ.get("API_BEARER_TOKEN")
    assert token, "Bearer token must be set as environment variable API_BEARER_TOKEN"
    return token

@pytest.fixture(scope="module")
def api_base_url():
    # Traceability: Ensure the API is reachable (preconditions)
    url = os.environ.get("API_BASE_URL", "https://api.example.com")
    return url.rstrip("/")

@pytest.fixture(scope="module")
def auth_header():
    return {
        "Authorization": f"Bearer {get_bearer_token()}",
        "Content-Type": "application/json"
    }

def test_delete_agent_invalid_id_schema(api_base_url, auth_header):
    """
    Traceability:
      - Standard: OWASP ASVS V10 (Error Handling), RFC 8259 (JSON RFC Compliance), ISO/IEC/IEEE 29148 (Requirements testability)
      - Source: openapi_spec : delete_agent_api_agents__agent_id__delete
      - Test Case: TC-DELETE-f2e6c865-007
    Validates that error responses match the specified HTTPValidationError schema and contain required fields on DELETE /api/agents/{agent_id} with an invalid id.
    """
    # Step 1: Send DELETE request with invalid agent id
    invalid_agent_id = "invalid!@#"  # intentionally malformed to trigger schema validation error
    endpoint = f"{api_base_url}/api/agents/{invalid_agent_id}"
    response = requests.delete(endpoint, headers=auth_header)

    # Expected results: Status code 422 or 404
    assert response.status_code in [422, 404], (
        f"Expected HTTP 422 or 404, got {response.status_code}. Traceable to OpenAPI/ASVS error handling."
    )

    # RFC 8259: Content-Type must be application/json
    assert response.headers.get("Content-Type", "").startswith("application/json"), (
        "Response Content-Type must be application/json as per RFC 8259."
    )

    # Parse and validate error schema
    json_error = response.json()
    # The OpenAPI/ASVS schema expects:
    # { "detail": [{"loc": [..], "msg": "str", "type": "str"}]} 
    assert "detail" in json_error, (
        "Response JSON must contain 'detail' key (ASVS V10, OpenAPI schema compliance)."
    )
    details = json_error["detail"]
    assert isinstance(details, list), ("'detail' field must be a list as per schema.")
    assert details, ("'detail' list should not be empty.")
    for err in details:
        # All required fields must be present
        for field in ("loc", "msg", "type"):
            assert field in err, f"Error detail must contain '{field}'."
        # Additional schema compliance
        assert isinstance(err["loc"], list), "'loc' should be a list (OpenAPI schema)."
        assert all(isinstance(loc_elm, (str, int)) for loc_elm in err["loc"]), (
            "Elements of 'loc' must be string or integer, per OpenAPI."
        )
        assert isinstance(err["msg"], str), "'msg' must be a string."
        assert isinstance(err["type"], str), "'type' must be a string."

    # Compliance tagging (not part of the assert, for audit/standards attestation):
    # OWASP ASVS V10 (Error Handling), RFC 8259 (JSON conformance), Requirement trace: ISO/IEC/IEEE 29148.
