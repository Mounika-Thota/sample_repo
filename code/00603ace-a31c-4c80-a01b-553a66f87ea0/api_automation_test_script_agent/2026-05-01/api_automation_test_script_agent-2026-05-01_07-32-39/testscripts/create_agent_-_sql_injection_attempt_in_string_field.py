import pytest
import requests
import os

ISO_29148_TRACEABILITY_ID = 'TC-POST-9a0eda3c-012'
OWASP_ASVS_REFS = ['V5', 'V10']
API_ENDPOINT = os.environ.get('API_ENDPOINT', 'https://api.example.com/api/agents/')
BEARER_TOKEN = os.environ.get('BEARER_TOKEN', '')
\****************(scope='module')
def api_headers():
    assert BEARER_TOKEN, 'Bearer token must be set in environment variable BEARER_TOKEN'  # ISO 29148: Verify precondition
    return {
        'Authorization': f'Bearer {BEARER_TOKEN}',
        'Content-Type': 'application/json'
    }
\****************(scope='module')
def injection_payload():
    """
    SQL injection string in 'slug' field, per test case and OWASP ASVS (V5: Input Validation)
    """
    return {
        'slug': "'; DROP TABLE agents; --",
        'display_name': 'Agent Injection',
        'category': 'testing'
    }
\**********************\************************\********************\*************.iso_iec_ieee_29148_id(ISO_29148_TRACEABILITY_ID)
def test_input_validation_sql_injection(api_headers, injection_payload):
    """
    Ensure API input validation prevents SQL injection via slug or display_name fields and returns a safe error.
    Compliant with OWASP ASVS (V5 Input Validation, V10 Error Handling), ISO/IEC/IEEE 29148 (traceability).
    Preconditions:
      - API is reachable
      - Valid Bearer token is available
    Steps:
      - Send POST request to /api/agents/ with potential SQL injection string in slug field
    Expected Results:
      - Status 422 or safe error returned
      - No server error or sensitive info is exposed
      - No injection occurs; database remains unaffected
    Traceability:
      - Testcase ID: TC-POST-9a0eda3c-012
      - OWASP ASVS: V5, V10
    """
    # Verify precondition: API reachable
    try:
        health_check = requests.options(API_ENDPOINT, headers=api_headers)
        assert health_check.status_code < 500, 'API endpoint unreachable or returns server error (ISO 29148)'  # RFC 8259: HTTP response codes
    except requests.RequestException as e:
        pytest.fail(f'API not reachable: {e}')

    # Send POST request with injection attempt
    response = requests.post(API_ENDPOINT, json=injection_payload, headers=api_headers)

    # Validate RFC 8259 and OWASP ASVS V5/V10: Proper error status code (not 500/502/503), input validation
    assert response.status_code in [422, 400], (
        f"Expected status code 422 or 400, got {response.status_code}. (OWASP ASVS V10, RFC 8259)"
    )
    
    # Validate safe error response (ISO 29148, OWASP ASVS V10): No sensitive info in error
    try:
        error_body = response.json()
    except ValueError:
        # RFC 8259: Ensure response is proper JSON
        pytest.fail('Error response is not valid JSON (RFC8259)')

    # Check typical safe error fields (not exhaustive)
    assert not any(
        keyword in str(error_body).lower() for keyword in ['exception', 'traceback', 'stack', 'sql', 'database', 'drop', 'agents']
    ), 'Error response must not expose sensitive information or internal errors (OWASP ASVS V10)'
    
    # Proper error message (ISO 29148): Should indicate input validation issue
    # Optionally check for existence of 'error', 'message', or 'detail' per API spec
    assert ('error' in error_body or 'message' in error_body or 'detail' in error_body), 'Response should provide a safe validation error message (ISO 29148, OWASP ASVS V10)'

    # The following check recommends DB query integrity, but cannot be fully verified via API alone
    # If available, check DB status via API (optional compliance step)
    # assert verify_agents_table_integrity(), 'Agents table altered -- injection occurred! (OWASP ASVS V5)'
    
    # Traceability (ISO/IEC/IEEE 29148): Attach test results to requirements refs
    print(f'ISO/IEC/IEEE 29148 TraceabilityID: {ISO_29148_TRACEABILITY_ID}, OWASP ASVS: {OWASP_ASVS_REFS}')
