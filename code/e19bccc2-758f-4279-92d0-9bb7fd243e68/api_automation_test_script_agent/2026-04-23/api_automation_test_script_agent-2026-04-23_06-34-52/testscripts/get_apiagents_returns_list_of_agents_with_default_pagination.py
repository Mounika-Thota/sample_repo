import pytest
import requests
from typing import Any, List

# Compliance references:
# - RFC 8259 (JSON response validation)
# - OWASP ASVS (V2: Authentication, V5: Validation, encoding and escaping)
# - ISO/IEC/IEEE 29148 (Requirements traceability and verification)

API_BASE_URL = "<REPLACE_WITH_API_BASE_URL>"
BEARER_TOKEN = "<REPLACE_WITH_TOKEN>"  # To be dynamically provided in CI or replaced in secure manner
\****************(scope="module")
def api_headers() -> dict:
    """
    Setup: Provide standard headers, validating the mandatory Authorization and Content-Type.
    Ensures traceability to: OWASP ASVS V2, V5.
    """
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    # Ensure no header has an empty value (OWASP ASVS)
    for k, v in headers.items():
        assert v.strip(), f"Header '{k}' must not be empty."
    return headers

def is_json(payload: Any) -> bool:
    """
    Verifies that the response is proper RFC 8259 compliant JSON.
    """
    if payload is None:
        return False
    if isinstance(payload, (dict, list)):
        return True
    return False
\*******************\************************\********************\*************.owasp_asvs(["V2", "V5"])
def test_get_agents_list_default(api_headers):
    """
    TC-GET-2f1c1c7e-001: Validate that GET /api/agents/ returns a list of agents with status 200 using default parameters.
    Requirements Traceability:
        - RFC 8259: Response must be valid JSON.
        - OWASP ASVS V2: Authorization header required.
        - OWASP ASVS V5: Validation on response structure and limit enforcement.
        - ISO/IEC/IEEE 29148: All requirements are assertable & traceable.
    """
    endpoint = f"{API_BASE_URL}/api/agents/"
    response = requests.get(endpoint, headers=api_headers)

    # Step 1: Status 200
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}."

    # Step 2: Response body is a JSON array or object representing agents
    try:
        data = response.json()
    except ValueError:
        pytest.fail("Response body is not valid RFC 8259 JSON.")
    assert is_json(data), "Response must be valid JSON array or object per RFC 8259."

    # Step 3: Response contains no more than 100 agents (default limit)
    # Defensive: Accept both array and object (as per requirement)
    agents_list: List[Any] = []
    if isinstance(data, list):
        agents_list = data
    elif isinstance(data, dict):
        # If agents are nested inside an object
        # Try to infer list via common keys
        candidates = [v for v in data.values() if isinstance(v, list)]
        assert len(candidates) > 0, "Cannot find agents array in response object."
        agents_list = candidates[0]  # Take first candidate
    else:
        pytest.fail("Response is neither an array nor object containing agents list.")
    assert len(agents_list) <= 100, f"Returned agents list size {len(agents_list)} exceeds default limit (100)."
    # Optionally: Validate that every agent is a dict/object, if possible
    for agent in agents_list:
        assert isinstance(agent, dict), "Every agent entry must be a JSON object (per OpenAPI, ISO/IEC/IEEE 29148 traceability)."

# No teardown needed as this is a GET request that does not create/modify data.