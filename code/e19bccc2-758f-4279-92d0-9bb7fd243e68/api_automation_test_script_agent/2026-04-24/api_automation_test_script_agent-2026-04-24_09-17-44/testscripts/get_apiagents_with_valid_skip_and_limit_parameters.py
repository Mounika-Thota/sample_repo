import pytest
import requests
from typing import List, Dict

# Standards Tracing (ISO/IEC/IEEE 29148):
# Requirements are mapped by test case ID 'TC-GET-2f1c1c7e-002'.
# RFC 8259 compliance: all JSON parsed with standards-compliant code.
# OWASP ASVS 4.0 References: V2 (Authentication), V5 (Validation & Encoding).

BASE_URL = "<REPLACE_WITH_BASE_URL>"   # Must be configured per environment
ENDPOINT = "/api/agents/"
\****************(scope="session")
def bearer_token():
    # This fixture must be implemented to fetch a valid token securely.
    # For compliance, do NOT hardcode secrets in codebase.
    # Example shown below; replace with secure vault integration.
    token = "<REPLACE_WITH_TOKEN>"
    assert token and token != "<REPLACE_WITH_TOKEN>", "Valid Bearer token must be supplied for OWASP ASVS V2 compliance."
    return token
\****************(scope="module")
def agents_list_all(bearer_token):
    """Retrieve the full, ordered list of agents for verifying pagination correctness."""
    # For traceability, fetch all without skip/limit to determine expected offset.
    url = BASE_URL + ENDPOINT
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    assert response.status_code == 200, f"Precondition failed: API returned unexpected {response.status_code}"
    data = response.json()
    assert isinstance(data, list), "Agents list (RFC 8259/OWASP V5) must return a JSON array."
    return data
\************************\************************\******************("V2")\******************("V5")
def test_pagination_offset_and_limit(bearer_token, agents_list_all):
    """
    TC-GET-2f1c1c7e-002: Validate that GET /api/agents/ returns paginated results when skip and limit query parameters are provided.
    ASVS V2: All calls require valid authentication.
    ASVS V5/RFC8259: All JSON structures must be valid and controlled by limit. No overflows, no untrusted data, verified schema.
    ISO/IEC/IEEE 29148: Verifiable requirement.
    """
    skip = 10
    limit = 5

    url = BASE_URL + ENDPOINT
    params = {"skip": skip, "limit": limit}
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, params=params, headers=headers)

    # 200 (OK) status code
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    # RFC 8259: Parse-valid JSON
    try:
        data = response.json()
    except ValueError as e:
        pytest.fail(f"Response body is not valid JSON (RFC 8259): {e}")

    # Agent response type: should be an array (or paged object w/ items list)
    if isinstance(data, list):
        agents = data
    elif isinstance(data, dict) and "items" in data:
        # Acceptable alternate pagination format
        agents = data["items"]
    else:
        pytest.fail("Response JSON structure is not a list or paginated object with 'items'. (OWASP ASVS V5, RFC8259)")

    # Limit: at most 5 results
    assert 0 <= len(agents) <= limit, f"Expected at most {limit} agents, got {len(agents)}"

    # Returned agents must correspond to correct offset (skip=10)
    # Compare to the baseline all-agents list
    expected_agents = agents_list_all[skip:skip+limit]
    # Verify paginated agents match slice of baseline by unique identifier (e.g., ID)
    if agents and expected_agents:
        agent_id_key = None
        for keyname in ['id', 'uuid', 'agent_id']:
            if keyname in agents[0] and keyname in expected_agents[0]:
                agent_id_key = keyname
                break
        assert agent_id_key, "Agent object does not have a recognizable unique identifier key (id/uuid/agent_id)."
        # Check that paginated IDs match
        paged_ids = [a[agent_id_key] for a in agents]
        expected_ids = [a[agent_id_key] for a in expected_agents]
        assert paged_ids == expected_ids, (
            f"Paginated agents do not match expected offset.\nExpected IDs: {expected_ids}\nReturned IDs: {paged_ids}"
        )

    # ISO/IEC/IEEE 29148: Each assertion is verifiable and traceable to requirements

def teardown_module(module):
    # No explicit teardown required; add any cleanup here as needed
    pass
