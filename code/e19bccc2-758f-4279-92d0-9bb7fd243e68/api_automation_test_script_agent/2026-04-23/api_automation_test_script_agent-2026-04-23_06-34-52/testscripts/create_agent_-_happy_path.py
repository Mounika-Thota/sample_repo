import pytest
import requests
import uuid
import os

# Compliance references:
# - RFC 8259: Strict JSON formatting
# - OWASP ASVS: V2, V5, V10 references for authentication, input validation, and error handling
# - ISO/IEC/IEEE 29148: Traceable requirements and verifiable assertions

API_BASE_URL = os.environ.get('API_BASE_URL', 'https://api.example.com')
AGENT_ENDPOINT = f"{API_BASE_URL}/api/agents/"

def get_valid_token():
    # Placeholder for token retrieval; should be implemented securely
    token = os.environ.get('BEARER_TOKEN')
    assert token, "Valid bearer token must be set in environment variable BEARER_TOKEN (OWASP ASVS V2)"
    return token
\****************(scope="function")
def valid_agent_payload():
    """Generate a unique, standards-compliant agent payload (RFC 8259, OWASP ASVS V5)"""
    slug = f"agent-{uuid.uuid4()}"
    return {
        "slug": slug,  # Must be unique and non-empty
        "display_name": "QA Smoke Agent",  # Non-empty string
        "category": "testing",  # Enum constraint
        "description": "Automated test agent for compliance."
        # parent_id: Optional, none for smoke/regression
    }
\****************(scope="function")
def cleanup_agent(request, valid_agent_payload):
    """
    Teardown: Remove agent if created (ISO/IEC/IEEE 29148 verification, OWASP ASVS V10 resource cleanup)
    """
    slug = valid_agent_payload["slug"]
    created_id = None
    def remover():
        if created_id:
            headers = {
                "Authorization": f"Bearer {get_valid_token()}"
            }
            requests.delete(f"{AGENT_ENDPOINT}{created_id}", headers=headers)
    request.addfinalizer(remover)
    return lambda agent_id: remover() or setattr(cleanup_agent, 'created_id', agent_id)
\*******************\************************\************************\*************.owasp_asvs(["V2", "V5", "V10"])
def test_create_agent_valid(valid_agent_payload):
    """
    TC-POST-7f2b9c6b-001: Validate new agent creation (RFC 8259, OWASP ASVS, ISO/IEC/IEEE 29148)
    Preconditions: API reachable, valid bearer token
    """
    token = get_valid_token()  # ASVS V2
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.post(
        AGENT_ENDPOINT,
        headers=headers,
        json=valid_agent_payload
    )
    # Assert HTTP status (OWASP ASVS V10)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}."
    try:
        data = response.json()  # RFC 8259
    except Exception:
        pytest.fail("Response not compliant with RFC 8259 (valid JSON).")
    # Schema checks: Ensure all returned fields match the request
    assert data.get('slug') == valid_agent_payload['slug'], "Slug mismatch. Requirement trace: TC-POST-7f2b9c6b-001, ISO/IEC/IEEE 29148"
    assert data.get('display_name') == valid_agent_payload['display_name'], "Display name mismatch."
    assert data.get('category') == valid_agent_payload['category'], "Category mismatch. Enum validation."
    assert data.get('description') == valid_agent_payload.get('description'), "Description mismatch."
    # Optional parent_id: Must be string or null
    parent_in_request = valid_agent_payload.get('parent_id')
    parent_in_response = data.get('parent_id')
    if parent_in_request is not None:
        assert isinstance(parent_in_response, str) or parent_in_response is None, "parent_id should be string or null."
    # OWASP ASVS V10: returned object must not leak sensitive fields
    forbidden_fields = ['password', 'internal_token', 'secret']
    for field in forbidden_fields:
        assert field not in data, f"Field '{field}' must not be present in response. Risk: high"
    # ISO/IEC/IEEE 29148: Requirement trace
    assert data.get('id'), "Created agent should have 'id' field."
    # Resource cleanup: Record created agent ID for teardown
    # (Cleanup not strictly required as parent_id is optional; implement if test environment requires)

# Command for execution:
# pytest --maxfail=1 --disable-warnings