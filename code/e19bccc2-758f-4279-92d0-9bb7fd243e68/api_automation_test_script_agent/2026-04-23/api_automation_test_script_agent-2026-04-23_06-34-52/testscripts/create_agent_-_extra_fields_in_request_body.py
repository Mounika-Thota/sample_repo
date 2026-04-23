import os
import pytest
import requests

# Standards Compliance:
# - RFC 8259 (JSON syntax compliance)
# - OWASP ASVS V5 (Validation, Sanitization)
# - OWASP ASVS V10 (Error handling, Validation)
# - ISO/IEC/IEEE 29148 traceability via test naming and documentation

API_BASE_URL = os.getenv('API_BASE_URL', 'https://api.example.com')
BEARER_TOKEN = os.getenv('BEARER_TOKEN')  # Must be supplied in environment or test fixtures
\****************(scope='session', autouse=True)
def check_prerequisites():
    """Precondition: API is reachable and valid bearer token is available."""
    assert BEARER_TOKEN, "Bearer token must be provided via the BEARER_TOKEN environment variable."
    health_endpoint = f"{API_BASE_URL}/health"
    try:
        r = requests.get(health_endpoint, timeout=5)
        assert r.status_code < 500, f"Service unreachable: GET {health_endpoint} returned {r.status_code}"
    except Exception as e:
        pytest.skip(f"API not reachable: {e}")
\****************
def agent_payload():
    """Create a valid agent payload with an extra unexpected field."""
    from uuid import uuid4
    slug = f"agent-extra-{uuid4().hex[:8]}"
    payload = {
        "slug": slug,
        "display_name": "Agent Extra",
        "category": "testing",
        "extra_field": "unexpected"
    }
    return payload
\*************.owasp_asvs(["V5", "V10"])\*************.iso_iec_29148("TC-POST-7f2b9c6b-018")
def test_extra_field_ignored_or_error(check_prerequisites, agent_payload):
    """
    TC-POST-7f2b9c6b-018: Validate that extra fields in request body are ignored or cause error as per spec.
    Standards: RFC 8259 for JSON, OWASP ASVS V5/V10, ISO/IEC/IEEE 29148 traceability.
    """
    endpoint = f"{API_BASE_URL}/api/agents/"
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.post(endpoint, json=agent_payload, headers=headers)
    status = response.status_code
    
    # -- RFC 8259: ensure body is valid JSON
    try:
        body = response.json()
    except Exception as e:
        pytest.fail(f"Response is not valid JSON (RFC 8259): {e}")
    
    # -- OWASP ASVS V5/V10: Check that extra fields are ignored or validation error is explicit
    assert status in [200, 422], f"Expected status 200 or 422, got {status}"

    if status == 200:
        # Server ignores extra field - ensure it is not present in response
        assert 'extra_field' not in body, (
            "Response should not echo 'extra_field' if it was ignored as per OpenAPI/ASVS V5"
        )
        # Also check success criteria (the main fields are present)
        for key in ['slug', 'display_name', 'category']:
            assert key in body, f"Expected '{key}' in response body"
    elif status == 422:
        # Server validates input and rejects extra field
        # Ensure error message refers to 'extra_field' and format is secure (ASVS V10)
        err_fields = str(body)
        assert 'extra_field' in err_fields, "Validation error should mention the unknown field (ASVS V5, V10)"
        # No sensitive internal details exposed
        assert 'Exception' not in err_fields and 'Traceback' not in err_fields, (
            "Error response must not leak internal details (ASVS V10)"
        )
    else:
        pytest.fail(f"Unexpected status code: {status}")
