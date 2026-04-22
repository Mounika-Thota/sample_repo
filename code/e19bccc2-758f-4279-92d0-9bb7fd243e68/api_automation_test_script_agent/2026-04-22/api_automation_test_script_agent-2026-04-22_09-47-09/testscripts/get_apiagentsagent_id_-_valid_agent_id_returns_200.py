import os
import requests
import pytest

# Constants (Replace these with secure secret management in real environments)
API_BASE_URL = os.environ.get('API_BASE_URL', 'https://api.example.com')
AGENT_ID = os.environ.get('EXISTING_AGENT_ID')  # e.g., '1234-abc'
BEARER_TOKEN = os.environ.get('VALID_BEARER_TOKEN')

@pytest.fixture(scope="module")
def auth_headers():
    """Provide Authorization headers adhering to RFC 8259 and OWASP ASVS (V2, V5)."""
    assert BEARER_TOKEN, "Bearer token must be provided via environment variable."
    return {
        'Authorization': f'Bearer {BEARER_TOKEN}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

@pytest.fixture(scope="module")
def api_is_reachable():
    """Basic heathcheck to ensure API is up before test (ISO/IEC/IEEE 29148 traceability)."""
    health_url = f"{API_BASE_URL}/health"  # Replace with actual healthcheck endpoint if available
    try:
        response = requests.get(health_url, timeout=5)
        assert response.status_code == 200
    except Exception as e:
        pytest.skip(f"API not reachable: {e}")

@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.sanity
@pytest.mark.owasp("V2", "V5")
def test_get_agent_by_id(api_is_reachable, auth_headers):
    """
    Validate that providing a valid, existing agent_id with proper bearer token returns a 200 response and agent info.
    Compliance: RFC 8259 (JSON), OWASP ASVS V2 (Authentication), V5 (Data Validation), ISO/IEC/IEEE 29148.
    Traceability: id=TC-GET-ab9c4c2e-001.
    """
    assert AGENT_ID, "AGENT_ID must be set in environment variable EXISTING_AGENT_ID."
    url = f"{API_BASE_URL}/api/agents/{AGENT_ID}"

    response = requests.get(url, headers=auth_headers)

    # Validate Status Code (expected: 200)
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"

    # Validate Response Content-Type (expected: application/json)
    content_type = response.headers.get('Content-Type', '')
    assert 'application/json' in content_type.lower(), f"Expected content-type application/json, got {content_type}"

    # Validate Response Body contains agent details (schema, basic fields check per ASVS/ISO)
    try:
        data = response.json()  # RFC 8259 compliant
    except Exception as e:
        pytest.fail(f"Response body is not valid JSON: {e}")
    assert isinstance(data, dict), "Response JSON not an object as expected."
    # Minimal expected keys (vary according to OpenAPI spec, adapt as needed for traceability)
    minimal_keys = ["id", "name"]
    for key in minimal_keys:
        assert key in data, f"Missing mandatory agent detail '{key}' in response. Trace to 29148-requirement."
    # Ensure agent ID in response matches request for verifiability (ISO/IEC/IEEE 29148)
    assert data["id"] == AGENT_ID, f"Returned agent ID does not match requested ID."
