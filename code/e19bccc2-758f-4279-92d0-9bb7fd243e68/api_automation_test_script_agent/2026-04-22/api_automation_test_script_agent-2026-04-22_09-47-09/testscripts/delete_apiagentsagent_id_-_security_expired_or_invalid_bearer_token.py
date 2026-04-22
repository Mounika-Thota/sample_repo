import pytest
import requests

# --- Configuration Section (adjust endpoint as needed) ---
BASE_URL = "https://api.example.com"  # TODO: Set API base URL

# Test constants. Replace with fixture-driven agent ID if needed.
@pytest.fixture(scope='module')
def agent_id():
    # Placeholder: replace this with code that creates/retrieves a valid agent as precondition if a real agent is needed.
    return "<REPLACE_WITH_AGENT_ID>"

@pytest.fixture(scope='module')
def expired_token():
    # Provide a known-expired, revoked, or syntactically invalid JWT/Token per environment's security policies.
    # Must NOT be a valid/active token.
    return "<REPLACE_WITH_EXPIRED_TOKEN>"

# Precondition: API is reachable
@pytest.fixture(scope='module')
def api_reachable():
    try:
        r = requests.get(f"{BASE_URL}/status", timeout=5)
        assert r.status_code < 500, "API is not reachable (Status: %s)" % r.status_code
    except Exception as exc:
        pytest.skip(f"Blocked: API not reachable: {exc}")

@pytest.mark.owasp_asvs('V2')
@pytest.mark.regression
@pytest.mark.sanity
@pytest.mark.security
@pytest.mark.risk_high
@pytest.mark.traceability(requirements=['RFC8259', 'OWASP ASVS V2', 'ISO/IEC/IEEE 29148'])
def test_delete_agent_with_expired_token(api_reachable, agent_id, expired_token):
    """
    Test Case: TC-DELETE-f2e6c865-009
    Description: Ensure the endpoint responds correctly to expired or invalid tokens. (OWASP ASVS V2)
    Compliance: RFC 8259 (JSON structure), ISO/IEC/IEEE 29148 (test requirement traceability)
    """
    endpoint = f"{BASE_URL}/api/agents/{agent_id}"
    headers = {
        "Authorization": f"Bearer {expired_token}",
        "Content-Type": "application/json"
    }

    response = requests.delete(endpoint, headers=headers)

    # --- Assertions in compliance with standards ---
    # RFC 8259: Ensure response is valid JSON, even on error.
    assert response.headers.get('Content-Type', '').startswith('application/json'), (
        "Response is not JSON (RFC 8259)"
    )
    
    # Status code is 401 (OWASP ASVS V2: Verify authentication/authorization is enforced)
    assert response.status_code == 401, f"Expected status 401 for unauthorized access, got {response.status_code}"
    
    # Body matches OpenAPI negative schema ({'detail': 'string'})
    resp_json = response.json()
    
    assert 'detail' in resp_json, "Response does not contain 'detail' field indicating authentication error as per schema"
    assert isinstance(resp_json['detail'], str), "'detail' field must be a string (RFC 8259 compliance)"
    
    # OWASP ASVS V2: Ensure no sensitive information is leaked in error detail
    sensitive_keywords = ["token", "password", "secret", "credential", "key"]
    detail_lc = resp_json['detail'].lower()
    for word in sensitive_keywords:
        assert word not in detail_lc, f"Error detail leaks sensitive term: {word} (OWASP ASVS)"
    
    # Additional traceability
    # ISO/IEC/IEEE 29148: Test requirements are directly mapped & verifiable above via pytest marker and assertion rationale.

def teardown_module(module):
    # No agent is actually deleted due to auth error -- no clean-up necessary for this security test.
    pass
