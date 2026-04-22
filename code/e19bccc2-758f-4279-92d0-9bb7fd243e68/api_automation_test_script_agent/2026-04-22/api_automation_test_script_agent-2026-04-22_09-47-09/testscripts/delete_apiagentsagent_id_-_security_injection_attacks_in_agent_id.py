import pytest
import requests
from jsonschema import validate, ValidationError

# Compliance & Traceability notes:
# - RFC 8259: Ensures JSON payloads and error validation use strict JSON parsing
# - OWASP ASVS V5/V10: Validates input handling and error responses to prevent injection attacks and information leakage
# - ISO/IEC/IEEE 29148: Test case structure aligns with requirements specification traceability

API_BASE_URL = "https://api.example.com"  # Replace with actual API base URL
auth_token = None

def setup_module(module):
    """Setup authentication for the test module"""
    global auth_token
    # Obtain token by secure means, do NOT hardcode credentials
    # For demonstration, assume the token is set externally or fetched securely
    # e.g., auth_token = fetch_valid_token()
    # Placeholder
    auth_token = "<REPLACE_WITH_TOKEN>"
    assert auth_token is not None, "Authentication token must be provided"

def teardown_module(module):
    """Cleanup if necessary"""
    pass

def get_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def test_delete_agent_sql_injection_resilience():
    # RFC 8259 — Ensure all communication is JSON, proper headers
    # OWASP ASVS V5 (Input Validation), V10 (Error Handling)
    # ISO/IEC/IEEE 29148 traceability: TC-DELETE-f2e6c865-008
    
    agent_id = "' OR '1'='1"  # Crafted value aiming at injection
    endpoint = f"{API_BASE_URL}/api/agents/{agent_id}"
    headers = get_headers(auth_token)
    
    response = requests.delete(endpoint, headers=headers)
    # Store response for all checks
    
    # Expected: status code 422 (Unprocessable Entity) or 404 (Not Found)
    assert response.status_code in [422, 404], f"Expected status 422 or 404, got {response.status_code}"
    
    # No unwanted system behavior or exposure
    # OWASP ASVS V10: Error responses must not leak stack traces or internal info
    try:
        resp_json = response.json()
        # RFC 8259: Confirm valid JSON
    except ValueError:
        pytest.fail("Response is not valid JSON as per RFC 8259")
    assert 'detail' in resp_json, "Response must contain 'detail' key per schema"
    
    # Error response matches validation schema
    expected_schema = {
        "type": "object",
        "properties": {
            "detail": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "loc": {
                            "type": "array",
                            "items": {"type": ["string", "integer"]}
                        },
                        "msg": {"type": "string"},
                        "type": {"type": "string"}
                    },
                    "required": ["loc", "msg", "type"]
                }
            }
        },
        "required": ["detail"]
    }
    try:
        validate(instance=resp_json, schema=expected_schema)
    except ValidationError as ve:
        pytest.fail(f"Response does not match expected schema: {ve.message}")

    # Defensive: Ensure no exposure (check for common leakage keywords)
    forbidden_patterns = ["traceback", "Exception", "StackTrace", "<html>", "database", "syntax error"]
    resp_str = str(resp_json)
    assert not any(pattern.lower() in resp_str.lower() for pattern in forbidden_patterns), \
        "Error response exposes sensitive internals, violating OWASP ASVS V10"

    # ISO/IEC/IEEE 29148: Traceability - Link test by ID
    # Test fully covers: id=TC-DELETE-f2e6c865-008, method=DELETE, endpoint=/api/agents/{agent_id}
