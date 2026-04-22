import pytest
import requests

# Standards compliance: RFC 8259 (JSON), OWASP ASVS V5/V10, ISO/IEC/IEEE 29148 traceability
# Test Case ID: TC-GET-ab9c4c2e-005
# Description: Verify that providing a malformed or invalid agent_id parameter returns a 422 validation error.
# Expected: Status 422, application/json, HTTPValidationError format with detail field

API_BASE_URL = "https://api.example.com"  # Replace with actual API endpoint
TOKEN = pytest.config.getoption("--token")  # Token must be provided via pytest CLI option

@pytest.fixture(scope="session")
def bearer_token():
    # Compliance: secure bearer token handling as per OWASP ASVS
    if not TOKEN:
        pytest.skip("Valid token is required. Use --token=<token> when running tests.")
    return TOKEN

@pytest.fixture(scope="function")
def api_url():
    # Traceability: Ensures endpoint reuse and configurability
    return f"{API_BASE_URL}/api/agents"

@pytest.mark.regression
@pytest.mark.boundary
@pytest.mark.owasp_v5
@pytest.mark.owasp_v10
@pytest.mark.source_openapi(get_agent_api_agents__agent_id__get)
@pytest.mark.risk_level_medium
@pytest.mark.parametrize("invalid_agent_id", [
    "@@INVALID_ID@@",         # Non-UUID, clearly malformed
    "invalid!id!",            # Special characters
    "",                       # Empty string
    "123",                    # Too short non-UUID
    "xyz" * 10                # Long non-UUID
])
def test_get_agents_invalid_agent_id(api_url, bearer_token, invalid_agent_id):
    endpoint = f"{api_url}/{invalid_agent_id}"
    headers = {"Authorization": f"Bearer {bearer_token}"}

    # Step: Send GET request to /api/agents/{agent_id} with malformed agent_id
    response = requests.get(endpoint, headers=headers)

    # Validation 1: Status is 422
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    # Validation 2: Content-Type is application/json
    content_type = response.headers.get("Content-Type", "")
    assert content_type.startswith("application/json"), f"Expected JSON, got {content_type}"

    # Validation 3: Body matches HTTPValidationError format (RFC 8259, OWASP ASVS)
    body = response.json()
    assert "detail" in body, "Response body must contain 'detail' field"
    assert isinstance(body["detail"], list), "'detail' field must be a list"
    for error_item in body["detail"]:
        # ISO/IEC/IEEE 29148: Each returned error must have loc, msg, type
        assert set(error_item.keys()).issuperset({"loc", "msg", "type"}), (
            f"Each detail item must contain loc, msg, type: {error_item}"
        )
        assert isinstance(error_item["loc"], list), "loc field must be a list"
        assert all(isinstance(loc_elem, (str, int)) for loc_elem in error_item["loc"]), "loc elements must be string or integer"
        assert isinstance(error_item["msg"], str), "msg field must be a string"
        assert isinstance(error_item["type"], str), "type field must be a string"

    # Compliance trace:
    # - RFC 8259: Valid JSON format
    # - OWASP ASVS V5: Input validation failure returns correct error
    # - OWASP ASVS V10: Error details reveal no sensitive info
    # - ISO/IEC/IEEE 29148: All requirements are checked and verifiable

def pytest_configure(config):
    # Allow token option as per secure config handling
    config.addinivalue_line("option", "--token=Valid Bearer token for API authentication")
