import pytest
import requests

# Test Metadata for traceability (per ISO/IEC/IEEE 29148)
TEST_CASE_ID = 'TC-GET-2f1c1c7e-003'
OWASP_ASVS_REFS = ['V2']
RFC_8259_COMPLIANT = True

API_BASE_URL = 'https://api.example.com'  # Change to the correct environment
ENDPOINT = '/api/agents/'
EXPECTED_STATUS_CODES = [401, 403]  # Per expected_results
\****************(scope='module')
def api_url():
    url = f"{API_BASE_URL}{ENDPOINT}"
    yield url
\**********************\******************\**********************\*************************("headers", [
    # Per RFC 8259, Content-Type header is allowed (JSON), Authorization intentionally omitted.
    {"Content-Type": "application/json"}
])
def test_get_agents_missing_auth(api_url, headers):
    """ TestCase ID: TC-GET-2f1c1c7e-003
        Description: Validate that GET /api/agents/ returns an authentication error when Authorization header is missing.
        OWASP ASVS Ref: V2 (Authentication)
        Standards: RFC 8259, ISO/IEC/IEEE 29148
        Precondition: API is reachable
        Steps:
        1. Send GET request to /api/agents/ without Authorization header.
        Validations:
        - Response status is 401 or 403
        - Response contains error message indicating missing or invalid authentication
    """

    response = requests.get(api_url, headers=headers)

    # Assert status code is 401 or 403 (OWASP ASVS requirement for failed authentication)
    assert response.status_code in EXPECTED_STATUS_CODES, (
        f"Expected status code 401 or 403, got {response.status_code} (trace: {TEST_CASE_ID})"
    )

    # RFC 8259: ensure response is valid JSON or carries correct Content-Type
    content_type = response.headers.get('Content-Type', '')
    assert 'application/json' in content_type, (
        f"Expected 'application/json' Content-Type, got '{content_type}' (trace: {TEST_CASE_ID})"
    )

    # Try parse as JSON (compliance with RFC 8259)
    try:
        response_json = response.json()
    except ValueError:
        pytest.fail(f"Response is not valid JSON as per RFC 8259 (trace: {TEST_CASE_ID})")

    # Error message must indicate missing or invalid authentication (ASVS ref, ISO/IEC/IEEE 29148 - requirement traceability)
    error_message = response_json.get('error') or response_json.get('message') or ""
    assert any(keyword in error_message.lower() for keyword in ["auth", "token", "credential", "missing", "invalid"]), (
        f"Response error message should indicate authentication failure (got: '{error_message}'; trace: {TEST_CASE_ID})"
    )

# No authentication or cleanup required.
