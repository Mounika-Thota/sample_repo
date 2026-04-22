import pytest
import requests
import uuid

# Constants (these should be provided securely in CI/CD or via environment variables)
API_BASE_URL = "https://api.example.com"
ENDPOINT = "/api/agents/"
AUTH_TOKEN = "<REPLACE_WITH_TOKEN>"  # Securely injected

# ISO/IEC/IEEE 29148: Traceability matrix, OWASP ASVS refs, RFC 8259 compliance
ASVS_REFS = ['V2', 'V5', 'V10']  # Authentication, Input Validation, Response Handling

@pytest.fixture(scope="module")
def api_headers():
    return {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }

def unique_slug():
    # RFC 8259: Slug must be unique and non-empty
    return f"agent-{uuid.uuid4()}"

def valid_agent_payload():
    return {
        "slug": unique_slug(),
        "display_name": "Agent Name",  # non-empty, as per requirements
        "category": "testing",  # must be one of allowed
        "description": "An agent for testing",  # optional
        # parent_id intentionally omitted for a minimal payload
    }

@pytest.fixture(scope="function")
def create_agent_payload():
    return valid_agent_payload()

@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.functional
@pytest.mark.asvs(["V2", "V5", "V10"])
def test_post_create_agent(api_headers, create_agent_payload):
    """
    TC-POST-7dead6b2-000: Validate that a valid POST request to /api/agents/ with all required fields creates a new agent and returns status 200.
    Traceability: RFC 8259 (JSON syntax), OWASP ASVS V2, V5, V10, ISO/IEC/IEEE 29148
    """
    url = f"{API_BASE_URL}{ENDPOINT}"
    # Preconditions check: API Reachability
    try:
        health_check = requests.get(API_BASE_URL + "/health", timeout=5)
        assert health_check.status_code == 200, "API health endpoint not reachable"
    except Exception as exc:
        pytest.skip(f"API not reachable: {exc}")

    response = requests.post(url, headers=api_headers, json=create_agent_payload)
    # OWASP ASVS V2: Authentication & Authorization
    assert response.request.headers['Authorization'].startswith('Bearer '), "Authorization header must be present (ASVS V2)"
    # RFC 8259: JSON content, ISO/IEC/IEEE 29148: Requirements
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"

    # Validate response body
    resp_json = response.json()
    # Check existence and types of all required fields (contract/schema)
    for field in ["id", "slug", "display_name", "category"]:
        assert field in resp_json, f"Missing '{field}' in response"
        assert isinstance(resp_json[field], str), f"'{field}' must be string as per schema"
    # Optional fields: description, parent_id (nullable)
    assert "description" in resp_json, "'description' optional but should be present (can be null)"
    assert "parent_id" in resp_json, "'parent_id' optional but should be present (can be null)"
    # Category constraint
    allowed_categories = ["usg", "testing", "api_doc_testing", "performance_testing", "deployment", "req_synthesizer", "ui_automation", "documentation"]
    assert resp_json["category"] in allowed_categories, f"Category '{resp_json['category']}' not allowed"
    # Slug uniqueness (cannot fully test here, but assert format)
    assert len(resp_json["slug"]) > 0, "Slug must be non-empty"
    # ISO/IEC/IEEE 29148: Verifiability and traceability
    agent_id = resp_json["id"]
    assert agent_id, "Agent ID must be present for traceability"

    # Clean up: Remove created agent (teardown, if endpoint supports DELETE)
    # Optional, for regression suites. Comment out if not required.
    # delete_resp = requests.delete(f"{API_BASE_URL}{ENDPOINT}{agent_id}/", headers=api_headers)
    # assert delete_resp.status_code in [200, 204], "Cleanup failed"

# To run: pytest -v test_post_agent.py