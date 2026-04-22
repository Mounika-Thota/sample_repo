import pytest
import requests

@pytest.fixture(scope="module")
def api_base_url():
    # Set this to your API base URL
    return "https://api.example.com"

@pytest.fixture(scope="module")
def bearer_token():
    # Implement retrieval of a valid Bearer token as per environment policy
    # Do NOT hard-code tokens - source securely or mock in secure test environment.
    return "<REPLACE_WITH_VALID_TOKEN>"

@pytest.fixture(scope="function")
def agent_id():
    # Provide a valid agent ID to test against.
    # Replace with logic to programmatically fetch/create a test agent if needed
    return "<REPLACE_WITH_AGENT_ID>"

def is_http_validation_error_schema(obj):
    """Validate object matches expected HTTPValidationError schema as per OpenAPI spec and RFC8259."""
    if not isinstance(obj, dict) or 'detail' not in obj:
        return False
    if not isinstance(obj['detail'], list):
        return False
    for entry in obj['detail']:
        if not isinstance(entry, dict):
            return False
        if 'loc' not in entry or 'msg' not in entry or 'type' not in entry:
            return False
        if not isinstance(entry['loc'], list):
            return False
        if not all(isinstance(x, (str, int)) for x in entry['loc']):
            return False
        if not isinstance(entry['msg'], str):
            return False
        if not isinstance(entry['type'], str):
            return False
    return True

def test_put_update_agent_validation_error_api8259_asvs10_29148(api_base_url, bearer_token, agent_id):
    """
    TC-PUT-55cdd53a-014: Ensure validation errors return a consistent schema and 'application/json' content type.
    Standards: RFC 8259 (JSON compliance), OWASP ASVS V10, ISO/IEC/IEEE 29148 (requirements traceability).
    """
    url = f"{api_base_url}/api/agents/{agent_id}"
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    # Craft an invalid enum value for 'category' as per OpenAPI spec
    payload = {"category": "invalid_enum_value"}

    response = requests.put(url, json=payload, headers=headers, timeout=10)

    # 1. Assert status code is 422
    assert response.status_code == 422, f"Expected 422 Unprocessable Entity, got {response.status_code}"

    # 2. Assert Content-Type is 'application/json; charset=utf-8' (RFC 8259 compliant JSON)
    content_type = response.headers.get("Content-Type", "")
    assert content_type.startswith("application/json"), f"Expected application/json Content-Type, got {content_type}"

    # 3. Assert response body matches the HTTPValidationError schema
    try:
        body = response.json()
    except Exception as e:
        pytest.fail(f"Response body is not valid JSON: {e}")
    assert is_http_validation_error_schema(body), f"Response body does not match documented HTTPValidationError schema: {body}"

    # (Traceability Note: Test covers RFC 8259 (JSON conformance), ASVS V10 (Error handling), ISO 29148 (unambiguous requirements)).
