import os
import pytest
import requests

# Constants (can be moved to config)
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.example.com")  # Should be provided via env/config
AUTH_TOKEN = os.getenv("API_AUTH_TOKEN")  # Should be injected securely

@pytest.fixture(scope='module')
def auth_header():
    # Precondition: Valid Bearer token available
    if not AUTH_TOKEN:
        pytest.skip("Valid Bearer token not set. Please export API_AUTH_TOKEN environment variable.")
    return {
        'Authorization': f'Bearer {AUTH_TOKEN}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

def validate_json_response_compliance(response):
    # RFC 8259 compliance: content-type and JSON decodability
    assert response.headers.get('Content-Type', '').startswith('application/json'), \
        "Content-Type header must be 'application/json' per RFC 8259"
    try:
        data = response.json()
    except ValueError:
        pytest.fail("Response body is not valid JSON as required by RFC 8259.")
    assert isinstance(data, list), \
        "Response body must be a JSON array/list (ISO/IEC/IEEE 29148, OpenAPI)."
    return data

def check_owasp_asvs_controls():
    # Minimal stub - integration with compliance traceability tools can be added
    # Example: V2 (Authentication) -- token present, must be used for all API calls
    assert AUTH_TOKEN is not None, "OWASP ASVS V2: Missing authentication bearer token."

@pytest.mark.regression
@pytest.mark.sanity
@pytest.mark.functional
@pytest.mark.owasp_asvs_v2
@pytest.mark.risk_medium
@pytest.mark.api
def test_get_agents_pagination(auth_header):
    """
    TC-GET-2e798b8e-01
    Validate that querying /api/agents/ with custom skip and limit returns correct paged results.
    Standards: RFC 8259, OWASP ASVS (V2), ISO/IEC/IEEE 29148
    """
    check_owasp_asvs_controls()
    url = f"{API_BASE_URL}/api/agents/"
    params = {
        'skip': 10,
        'limit': 15
    }
    # Step: Send GET request with auth
    response = requests.get(url, headers=auth_header, params=params, timeout=15)
    
    # Expected Result: Status 200
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    
    # Expected Results: Response body is JSON array/list of agents
    agents = validate_json_response_compliance(response)
    
    # Expected: Up to `limit` results in array, unless less remain
    assert len(agents) <= params['limit'], \
        f"Expected no more than {params['limit']} agents, got {len(agents)}"
    
    # The structure of each agent can be optionally validated with a schema if available
    # (ISO/IEC/IEEE 29148 - requirements traceability). For this test, only type/structure is checked
    for agent in agents:
        assert isinstance(agent, dict), "Each agent item must be a JSON object (OpenAPI, RFC 8259)"
    # Traceability: testcase id, RFC 8259, OWASP ASVS V2, ISO/IEC/IEEE 29148
