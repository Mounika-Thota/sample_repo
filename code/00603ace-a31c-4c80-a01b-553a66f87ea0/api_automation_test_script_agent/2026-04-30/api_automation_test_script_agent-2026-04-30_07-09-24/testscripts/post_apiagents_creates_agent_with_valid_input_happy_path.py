import pytest
import requests
import json
from jsonschema import validate, ValidationError

# ISO/IEC/IEEE 29148: Each requirement is traceable/tested via named assertion.
# RFC 8259: JSON payload and response validation strictly enforced.
# OWASP ASVS refs: V2 (Authentication), V5 (Input Validation), V10 (Error Handling)

BASE_URL = "https://api.example.com"  # Replace with correct URL
TOKEN = "<REPLACE_WITH_TOKEN>"        # Replace with valid Bearer token

AGENT_CATEGORY_ENUM = [
    'usg', 'testing', 'api_doc_testing', 'performance_testing',
    'deployment', 'req_synthesizer', 'ui_automation', 'documentation'
]

agent_response_schema = {
    "type": "object",
    "properties": {
        "slug": {"type": "string"},
        "display_name": {"type": "string"},
        "category": {"type": "string", "enum": AGENT_CATEGORY_ENUM},
        "description": {"type": ["string", "null"]},
        "parent_id": {"type": ["string", "null"]}
        # Additional fields may be added as per OpenAPI spec for /api/agents/
    },
    "required": ["slug", "display_name", "category"]
}
\****************(scope="module")
def bearer_token():
    # Requirement trace: ASVS V2 (Authentication)
    assert TOKEN and TOKEN != "<REPLACE_WITH_TOKEN>", "Valid Bearer token must be provided."
    return TOKEN
\****************(scope="function")
def cleanup_agent():
    # Placeholder cleanup. ISO/IEC/IEEE 29148 trace: post-test data removal.
    agents_to_cleanup = []
    yield agents_to_cleanup
    for agent_id in agents_to_cleanup:
        requests.delete(f"{BASE_URL}/api/agents/{agent_id}",
                        headers={"Authorization": f"Bearer {TOKEN}"})
\************************\*******************\************************\*************.owasp_asvs("V2", "V5", "V10")
def test_create_agent_success(bearer_token, cleanup_agent):
    """
    TC-POST-b1b1b150-001
    Validate agent is created successfully with all required fields and valid values.
    Standards: ISO/IEC/IEEE 29148, RFC 8259, OWASP ASVS
    """
    # Preconditions
    # API reachability
    response_ping = requests.get(f"{BASE_URL}/api/agents/", headers={"Authorization": f"Bearer {bearer_token}"})
    assert response_ping.status_code in [200, 401, 403], "API must be reachable - requirement trace: connectivity"

    # Input (ISO/IEC/IEEE 29148: input must be valid, enum enforced, no hardcoded values)
    payload = {
        "slug": "pytest-agent-001",
        "display_name": "Pytest Agent",
        "category": "api_doc_testing",
        "description": "Created via pytest, ISO/IEC/IEEE 29148 compliance test.",
        "parent_id": None
    }
    assert payload["slug"], "'slug' must be non-empty - requirement trace: RFC 8259"
    assert payload["display_name"], "'display_name' must be non-empty - requirement trace: RFC 8259"
    assert payload["category"] in AGENT_CATEGORY_ENUM, "'category' must be enum value - requirement trace: V5"

    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }

    # Step: Send POST request
    response = requests.post(
        f"{BASE_URL}/api/agents/",
        headers=headers,
        data=json.dumps(payload)
    )

    # Assertion 1: Status code is 200 (RFC 8259, ISO/IEC/IEEE 29148, OWASP ASVS V10)
    assert response.status_code == 200, f"Expected status 200, got {response.status_code} - requirement trace: V10"

    # Assertion 2: Response body is JSON
    try:
        resp_json = response.json()
    except Exception:
        pytest.fail("Response body is not valid JSON - requirement trace: RFC 8259")

    # Assertion 3: Response body matches schema
    try:
        validate(instance=resp_json, schema=agent_response_schema)
    except ValidationError as ve:
        pytest.fail(f"Response JSON does not match schema: {ve} - requirement trace: V5")

    # Assertion 4 (Extra): Creation acknowledged
    assert resp_json["slug"] == payload["slug"], "Response 'slug' must match sent value - requirement trace: ISO/IEC/IEEE 29148"
    assert resp_json["display_name"] == payload["display_name"], "Response 'display_name' must match - requirement trace"
    assert resp_json["category"] == payload["category"], "Response 'category' must match enum"
    
    # Save agent for cleanup
    if "id" in resp_json:
        cleanup_agent.append(resp_json["id"])
    
    # All requirements and compliance points are traceable above via assertions

