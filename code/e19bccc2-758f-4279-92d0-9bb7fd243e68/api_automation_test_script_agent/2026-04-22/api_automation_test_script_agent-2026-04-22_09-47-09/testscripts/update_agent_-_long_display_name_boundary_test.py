import pytest
import requests
import string
import random

API_BASE_URL = "https://api.example.com"  # Replace with actual base URL
AGENT_ID = "<REPLACE_WITH_AGENT_ID>"     # Replace with environment/config
BEARER_TOKEN = "<REPLACE_WITH_TOKEN>"    # Replace with secure retrieval method

@pytest.fixture(scope="module")
def auth_headers():
    """
    Setup Authorization and Content-Type headers as per RFC 8259
    """
    return {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }

@pytest.fixture(scope="module")
def long_display_name():
    """
    Create a 1024-character display_name value (boundary test)
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=1024))

@pytest.fixture(scope="module")
def agent_exists():
    """
    Verify the agent exists before attempting update (precondition, traceable to ISO/IEC/IEEE 29148: requirement validation)
    """
    url = f"{API_BASE_URL}/api/agents/{AGENT_ID}"
    response = requests.get(url, headers={"Authorization": f"Bearer {BEARER_TOKEN}"})
    assert response.status_code == 200, "Agent does not exist. Precondition failure."
    return True

@pytest.mark.boundary
@pytest.mark.regression
@pytest.mark.asvs("V5", "V10")
def test_update_agent_long_display_name(auth_headers, long_display_name, agent_exists):
    """
    Test updating agent with a very long display_name (1024 chars).
    Compliance: RFC 8259 (JSON), OWASP ASVS (V5: Input validation, V10: Error handling)
    Traceability: ISO/IEC/IEEE 29148 (functional, boundary, and error requirements)
    """
    url = f"{API_BASE_URL}/api/agents/{AGENT_ID}"
    payload = {"display_name": long_display_name}
    # Execute PUT (step: Send PUT request)
    response = requests.put(url, headers=auth_headers, json=payload)
    # System may allow or reject long value
    assert response.status_code in [200, 422], f"Expected 200 or 422, got {response.status_code}"  # RFC8259: status code
    
    if response.status_code == 200:
        # Verify updated display_name
        data = response.json()
        assert 'display_name' in data, "Response missing display_name"
        assert len(data['display_name']) == 1024, "display_name length mismatch in response"
        # ISO/IEC/IEEE 29148: requirement satisfied
    elif response.status_code == 422:
        # Validate error schema (OWASP ASVS V10, RFC 8259)
        err = response.json()
        assert 'errors' in err or 'error' in err, "422 response does not conform to expected error schema"
        # Check proper error messaging about display_name length
        errors = err.get('errors', [err.get('error')])
        assert any('display_name' in str(e) for e in errors if e), "Error does not reference display_name"
        # ISO/IEC/IEEE 29148: boundary error requirement

@pytest.fixture(scope="module", autouse=True)
def cleanup_agent_display_name():
    """
    Teardown: revert display_name to original value after test (traceability: requirement maintainability, compliance)
    """
    yield
    # Optionally revert if needed (not implemented due to lack of schema details)
    # Example:
    # requests.put(f"{API_BASE_URL}/api/agents/{AGENT_ID}", headers=auth_headers(), json={"display_name": "OriginalAgent"})
    #pass
