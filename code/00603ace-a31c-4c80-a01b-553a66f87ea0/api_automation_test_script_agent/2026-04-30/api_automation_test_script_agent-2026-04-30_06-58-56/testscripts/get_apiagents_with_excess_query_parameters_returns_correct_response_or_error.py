import pytest
import requests
from typing import Dict, Any

# --- Configuration (Could be parameterized externally for compliance and traceability) ---
BASE_URL = "https://api.example.com"  # Replace with actual API base URL
AUTH_TOKEN = "<REPLACE_WITH_TOKEN>"   # Should be provided securely via environment or CI secrets
ENDPOINT = "/api/agents/"

# --- RFC8259 (JSON format compliance asserts), ISO/IEC/IEEE 29148 (traceable requirements), OWASP ASVS (input validation checks) ---

VALIDATION_ERROR_SCHEMA = {
    "type": "object",
    "properties": {
        "detail": {"type": "array"}
    },
    "required": ["detail"]
}
\****************(scope="module")
def api_headers() -> Dict[str, str]:
    """
    Prepare authorization and content headers for API requests.
    Fulfills: ISO/IEC/IEEE 29148 - Requirement for precondition and security (OWASP ASVS V5, V10).
    """
    assert AUTH_TOKEN != "<REPLACE_WITH_TOKEN>", "Bearer token must be securely provided."
    return {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }

def validate_httpvalidationerror_schema(error_body: Dict[str, Any]):
    """
    Ensure error response matches the expected HTTPValidationError schema.
    Compliant with RFC8259 (JSON response) and ISO/IEC/IEEE 29148 for unambiguous requirements.
    """
    assert isinstance(error_body, dict), "Error body must be a JSON object."
    assert "detail" in error_body, "Validation error response must include 'detail'."
    assert isinstance(error_body["detail"], list), "'detail' must be a list."
\************************\**********************\*************.owasp_asvs(["V5", "V10"])
def test_get_agents_with_unexpected_query_params(api_headers):
    """
    Test Case: TC-GET-feb8d5e2-08
    Description: Validate GET /api/agents/ with unexpected query parameters handles gracefully (either ignores or returns validation error).
    Traceability:
      - Standard: ISO/IEC/IEEE 29148 (verifiable, unambiguous requirements)
      - Format: RFC 8259 (JSON)
      - Security: OWASP ASVS (V5: Access control, V10: Error handling)
    Preconditions: API is reachable, Valid Bearer token is available
    Steps:
      1. Send GET request to /api/agents/?foo=bar&skip=0&limit=10 with Authorization header
    Expected Results:
      - Status 200 or 422
      - If 200: response ignores unknown parameters
      - If 422: error body matches HTTPValidationError schema
    """
    params = {
        "foo": "bar",     # Unexpected param (boundary/robustness)
        "skip": 0,        # Known param
        "limit": 10       # Known param
    }
    response = requests.get(f"{BASE_URL}{ENDPOINT}", headers=api_headers, params=params)
    
    assert response.status_code in [200, 422], f"Unexpected status code: {response.status_code}"

    # Compliance: RFC 8259 (JSON) validation
    try:
        resp_json = response.json()
    except ValueError:
        pytest.fail("Response is not valid RFC8259-compliant JSON.")

    if response.status_code == 200:
        # Must ignore unknown parameter 'foo' (robustness principle)
        # Make the same request without the 'foo' param and compare results (excluding possible fields that can change, e.g., timestamps)
        params_control = {
            "skip": 0,
            "limit": 10
        }
        control_response = requests.get(f"{BASE_URL}{ENDPOINT}", headers=api_headers, params=params_control)
        assert control_response.status_code == 200, "Control request without unexpected parameter should succeed."
        try:
            control_json = control_response.json()
        except ValueError:
            pytest.fail("Control response is not valid RFC8259-compliant JSON.")
        # For simple idempotent list endpoints, result sets should match
        assert resp_json == control_json, (
            "Response with unexpected parameter differs from control (parameter should be ignored)."
        )
    elif response.status_code == 422:
        # Must conform to HTTPValidationError schema for RFC8259, OWASP ASVS V10 error handling
        validate_httpvalidationerror_schema(resp_json)
