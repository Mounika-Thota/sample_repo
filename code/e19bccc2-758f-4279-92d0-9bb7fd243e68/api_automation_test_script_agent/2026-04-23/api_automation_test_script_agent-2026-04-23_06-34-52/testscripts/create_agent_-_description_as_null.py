import pytest
import requests

# Constants for compliance
RFC_8259_COMPLIANT_HEADERS = {
    "Content-Type": "application/json"
}
OWASP_ASVS_REF = "V5"

# Test configuration
API_BASE_URL = "https://api.example.com"  # Update if needed
ENDPOINT = "/api/agents/"
\****************(scope='module')
def api_token():
    # Implement secure retrieval or mock of bearer token (ISO/IEC/IEEE 29148: traceability)
    # For the sake of compliance, do NOT hard-code sensitive info. Instead, use environment variables.
    import os
    token = os.environ.get("API_BEARER_TOKEN")
    assert token, "Valid bearer token must be set in environment variable API_BEARER_TOKEN"
    return token
\****************(scope='function')
def cleanup_agent():
    # Setup: No setup required before test
    # Teardown: Remove agent to avoid pollution (ISO/IEC/IEEE 29148: lifecycle traceability)
    agents_created = []
    yield agents_created
    for agent in agents_created:
        requests.delete(f"{API_BASE_URL}{ENDPOINT}{agent['slug']}", headers={
            "Authorization": f"Bearer {agent['token']}",
            "Content-Type": "application/json"
        })
\************************\********************\**********************
def test_create_agent_with_null_description(api_token, cleanup_agent):
    """ASVS V5, ISO/IEC/IEEE 29148 Traceable: Validate agent creation with explicit null description (RFC 8259 compliant)."""
    url = f"{API_BASE_URL}{ENDPOINT}"

    payload = {
        "slug": "agent-007",              # should be unique, non-empty
        "display_name": "Agent Seven",    # should be non-empty
        "category": "performance_testing",    # should be valid enum value
        "description": None                # explicit null (RFC 8259 compliance)
    }

    headers = {
        "Authorization": f"Bearer {api_token}",
        **RFC_8259_COMPLIANT_HEADERS
    }

    response = requests.post(url, json=payload, headers=headers)

    # --- BEGIN VALIDATION (standards traceable) ---
    # 1. Status 200
    assert response.status_code == 200, f"Expected 200, got {response.status_code} ({response.text})"

    # 2. Response body contains agent details and description as null
    resp_json = response.json()
    assert "description" in resp_json, "Response must contain 'description' field (RFC 8259)"
    assert resp_json["description"] is None, "'description' should be null as set in request"

    assert resp_json["slug"] == payload["slug"], "'slug' in response must match request"
    assert resp_json["display_name"] == payload["display_name"], "'display_name' in response must match request"
    assert resp_json["category"] == payload["category"], "'category' in response must match request"
    # Compliance: All fields validated as per OpenAPI spec, RFC 8259, ISO/IEC/IEEE 29148 traceability

    # Register for cleanup
    cleanup_agent.append({"slug": payload["slug"], "token": api_token})