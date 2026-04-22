import pytest
import requests

BASE_URL = "https://api.example.com"  # Replace with actual URL
TOKEN = "<REPLACE_WITH_TOKEN>"       # Replace securely during runtime or fixture

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

DUPLICATE_SLUG = "duplicate-slug"
DUPLICATE_AGENT_BODY = {
    "slug": DUPLICATE_SLUG,
    "display_name": "Agent Duplicate",
    "category": "usg"
}

CREATE_AGENT_ENDPOINT = f"{BASE_URL}/api/agents/"

@pytest.fixture(scope='module')
def ensure_agent_exists():
    """
    Fixture to ensure an agent with the duplicate slug exists prior to the test.
    Idempotent: handles 201, 409, or 422 responses gracefully.
    """
    response = requests.post(
        CREATE_AGENT_ENDPOINT,
        headers=HEADERS,
        json=DUPLICATE_AGENT_BODY,
        timeout=10
    )
    assert response.status_code in [201, 409, 422], \
        f"Setup failed: Unexpected status {response.status_code}, body: {response.text}"
    # No explicit teardown: created data is reused by this negative case.

@pytest.mark.regression
@pytest.mark.negative
@pytest.mark.owasp_asvs(['V5', 'V10'])
def test_create_agent_with_duplicate_slug_fails(ensure_agent_exists):
    """
    Validate POST /api/agents/ fails with 422 or 409 when creating an agent with duplicate slug. 
    Compliance: RFC 8259 (JSON), OWASP ASVS (V5, V10), ISO/IEC/IEEE 29148.
    Traceability: TC-POST-7dead6b2-005
    """
    # Step: Send POST request to /api/agents/ with duplicate slug
    response = requests.post(
        CREATE_AGENT_ENDPOINT,
        headers=HEADERS,
        json=DUPLICATE_AGENT_BODY,
        timeout=10
    )
    # Status code must be 422 (Unprocessable Entity) or 409 (Conflict)
    assert response.status_code in [422, 409], \
        f"Expected status 422 or 409, got {response.status_code}, body: {response.text}"
    
    # Body must be a compliant RFC 8259 JSON response, and contain error detail about duplicate slug
    try:
        body = response.json()
    except ValueError as e:
        pytest.fail(f"Response is not valid JSON (RFC 8259): {e}\nResponse: {response.text}")
    
    assert 'detail' in body, "Missing 'detail' in error response as per API spec."
    assert isinstance(body['detail'], list), "'detail' should be a list per contract."
    duplicate_error_found = False
    for error_item in body['detail']:
        assert isinstance(error_item, dict), "Each 'detail' item must be an object (per schema)."
        assert {'loc', 'msg', 'type'}.issubset(set(error_item)), \
            f"Error item missing expected keys. Found: {error_item.keys()}"
        assert 'slug' in ''.join(str(v) for v in error_item['loc']).lower(), \
            "Error location should reference 'slug' field."
        if 'duplicate' in error_item['msg'].lower():
            duplicate_error_found = True
    assert duplicate_error_found, "No error message about duplicate slug present."
    # Additional: Verifiability and traceability checks can be added here for standards compliance.
