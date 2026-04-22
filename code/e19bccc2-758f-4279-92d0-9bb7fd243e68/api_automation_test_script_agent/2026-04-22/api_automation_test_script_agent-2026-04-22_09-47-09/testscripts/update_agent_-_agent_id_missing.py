import os
import pytest
import requests

API_BASE_URL = os.environ.get('API_BASE_URL', 'https://api.example.com')
BEARER_TOKEN = os.environ.get('BEARER_TOKEN')

@pytest.fixture(scope='module')
def auth_headers():
    """
    Provides Authorization and Content-Type headers.
    Ensures Bearer token is supplied securely.
    """
    assert BEARER_TOKEN is not None, "Bearer token must be set as environment variable BEARER_TOKEN for compliance with RFC 8259/OWASP ASVS."
    return {
        'Authorization': f'Bearer {BEARER_TOKEN}',
        'Content-Type': 'application/json'
    }

def test_put_agents_missing_agent_id_returns_404_or_405(auth_headers):
    """
    Validate 404 or 405 is returned when agent_id path parameter is missing in PUT /api/agents/
    - OWASP ASVS v10 (Error handling)
    - RFC 8259 (JSON compliance)
    - ISO/IEC/IEEE 29148 - Requirement traceable by testcase ID TC-PUT-55cdd53a-007
    """
    url = f"{API_BASE_URL}/api/agents/"  # Intentionally missing agent_id path param for negative test
    request_body = {}  # Per OpenAPI source, we won't provide body params unless strictly required

    response = requests.put(url, headers=auth_headers, json=request_body)

    # Traceability: TC-PUT-55cdd53a-007 | api: update_agent_api_agents__agent_id__put
    assert response.status_code in [404, 405], f"Expected 404 or 405 per ASVS error handling, got {response.status_code}. Response: {response.text}"

    # RFC 8259 and ASVS: If JSON, parse and check structure
    content_type = response.headers.get('Content-Type', '')
    if 'application/json' in content_type:
        try:
            resp_json = response.json()
        except ValueError:
            pytest.fail(f"Content-Type is JSON but body is not valid JSON (RFC 8259)")
        # Optionally, assert error message/keys if your spec defines them
        # e.g., assert 'error' in resp_json

    # ISO/IEC/IEEE 29148 - requirement verifiability: Test ID, expected output verified by assertion.

def teardown_module(module):
    # No explicit data cleanup required as this is a negative (no resource created/modified). Ensure alignment with ISO/IEC/IEEE 29148.
    pass
