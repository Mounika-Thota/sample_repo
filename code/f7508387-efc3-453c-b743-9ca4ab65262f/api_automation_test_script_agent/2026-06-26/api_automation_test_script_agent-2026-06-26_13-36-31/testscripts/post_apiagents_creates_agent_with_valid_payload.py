import pytest
import requests
import uuid
import os

BASE_URL = os.environ.get("API_BASE_URL", "https://api.example.com")
AUTH_TOKEN = os.environ.get("API_BEARER_TOKEN")

REQUIRED_CATEGORY_ENUM = [
    "usg", "testing", "api_doc_testing", "performance_testing",
    "deployment", "req_synthesizer", "ui_automation", "documentation"
]

def generate_unique_slug():
    """
    Generates a slug that is guaranteed to be unique for each test run.
    RFC 8259: Ensures valid JSON, ISO/IEC/IEEE 29148: Traceable input data
    """
    return f"agent-{uuid.uuid4().hex[:8]}"

def get_headers():
    """
    Build required headers with environment-injected Bearer token. Enforces OWASP ASVS V2,V5, and V10.
    """
    assert AUTH_TOKEN, "Bearer token must be set in API_BEARER_TOKEN environment variable (ASVS V2, V10)."
    return {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }

def build_valid_payload():
    """
    Constructs a fully valid request payload, per ISO/IEC/IEEE 29148 traceability, and category enum.
    """
    return {
        "slug": generate_unique_slug(),
        "display_name": "Main Test Agent",
        "category": "testing"
    }

def validate_creation_response(resp_json, req_payload):
    """
    Placeholder for response schema validation. Ensures RFC 8259 compliance
    and optionally echoes created entity. Assumes the server echos request data.
    """
    for k in ("slug", "display_name", "category"):
        assert k in resp_json, f"Field '{k}' missing in response body (ISO/IEC/IEEE 29148, ASVS V5)"
        assert resp_json[k] == req_payload[k], f"Mismatch in response field '{k}' (ISO/IEC/IEEE 29148)"
    # Category should be one of allowed enum
    assert resp_json["category"] in REQUIRED_CATEGORY_ENUM, "Response category outside enum (ASVS V5.3.4)"

def delete_agent(slug):
    """
    Cleanup helper. Tears down created agent to maintain system state. Optional: Assumes DELETE /api/agents/{slug} is available.
    """
    del_url = f"{BASE_URL}/api/agents/{slug}"
    requests.delete(del_url, headers=get_headers())
\****************(scope="function")
def created_agent_slug(request):
    created = dict()
    def fin():
        # Attempt agent deletion if created
        slug = created.get("slug")
        if slug:
            delete_agent(slug)
    request.addfinalizer(fin)
    return created

def test_create_agent_success(created_agent_slug):
    """
    ISO/IEC/IEEE 29148 - Requirements Traceability
    RFC 8259      - JSON request/response
    OWASP ASVS    - V2 (authentication), V5 (validation), V10 (security)
    """
    # Preconditions
    # API is reachable
    health = requests.get(f"{BASE_URL}/health")
    assert health.status_code < 400, "API not reachable (ASVS V10.2.4)"
    # Valid Bearer token is available
    headers = get_headers()

    # Step: Prepare valid agent payload
    payload = build_valid_payload()
    created_agent_slug["slug"] = payload["slug"]

    # Step: Send POST request
    url = f"{BASE_URL}/api/agents/"
    response = requests.post(url, json=payload, headers=headers)

    # Expected Result: Status 200
    assert response.status_code == 200, f"Expected 200, got {response.status_code} (ASVS V5.1.4)"
    # Parse and validate response (RFC 8259)
    try:
        resp_json = response.json()
    except Exception as e:
        pytest.fail(f"Response body is not valid JSON (RFC 8259): {e}")

    # Expected Result: Response body matches creation schema or is an echo
    validate_creation_response(resp_json, payload)
