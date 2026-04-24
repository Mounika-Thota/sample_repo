import pytest
import requests
import os

BASE_URL = os.getenv('API_BASE_URL', 'https://api.example.com')
TOKEN = os.getenv('API_BEARER_TOKEN')
\****************(scope='module')
def auth_header():
    """Provides a valid Authorization header as per test precondition."""
    assert TOKEN is not None, 'Valid bearer token is required and must be set in API_BEARER_TOKEN env variable.'
    return {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }
\****************(scope='module')
def api_reachable():
    """Checks if API is reachable as per test precondition."""
    health_url = f"{BASE_URL}/health"
    resp = requests.get(health_url)
    assert resp.status_code in [200, 204], 'API health endpoint is not reachable.'
\************************\********************\*************.owasp_asvs('V5', 'V10')\*************.risk_level('medium')
def test_post_agents_missing_category(api_reachable, auth_header):
    """
    TC-POST-7f2b9c6b-004
    Validate error response when category is missing from request body.
    Standards: RFC 8259 (JSON validity), OWASP ASVS (V5, V10), ISO/IEC/IEEE 29148 (Requirements traceability)
    """
    endpoint = f"{BASE_URL}/api/agents/"
    # Construct body omitting 'category' as per requirement
    payload = {
        'slug': 'agent-004',
        'display_name': 'Agent Four'
    }

    # Step: Send POST request
    response = requests.post(endpoint, headers=auth_header, json=payload)

    # Traceability: Expected status code 422 (unprocessable entity)
    assert response.status_code == 422, f"Expected HTTP 422, got {response.status_code}"

    # RFC 8259: Ensure response is valid JSON
    try:
        resp_json = response.json()
    except ValueError:
        pytest.fail('Response body is not valid JSON (RFC 8259 compliance).')

    # ISO/IEC/IEEE 29148: Validate error field traceability
    assert 'detail' in resp_json, "Response body must contain 'detail' key per API spec."
    assert isinstance(resp_json['detail'], list), "'detail' must be a list, per schema."

    # OWASP ASVS V5: Validate structured error for missing category
    validation_error_found = any(
        (('category' in str(item.get('loc', []))) or ('category' in str(item.get('msg', ''))))
        and item.get('type') == 'value_error.missing'
        for item in resp_json['detail']
    )
    assert validation_error_found, "Validation error for 'category' missing must be present in 'detail', per OWASP ASVS error handling requirements."
