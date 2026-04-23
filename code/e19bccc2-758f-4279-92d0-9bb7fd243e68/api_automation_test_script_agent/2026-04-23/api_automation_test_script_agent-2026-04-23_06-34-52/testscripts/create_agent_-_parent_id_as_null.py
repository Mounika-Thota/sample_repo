import pytest
import requests
import uuid
import os

declare_rfc_8259 = 'RFC 8259 (JSON), compliance: All request and response payloads must adhere strictly to the JSON standards.'
declare_owasp_asvs_v5 = 'OWASP ASVS V5, compliance: API access control, authentication, and authorization must be robust and traceable.'
declare_iso_29148 = 'ISO/IEC/IEEE 29148, compliance: All requirements are traceable and test case IDs are referenced.'

BASE_URL = os.getenv('API_BASE_URL', 'https://api.example.com')  # Should be set in environment for production/test
BEARER_TOKEN = os.getenv('API_BEARER_TOKEN', '<REPLACE_WITH_TOKEN>')  # Must be valid for test run
\****************(scope="module")
def auth_headers():
    """
    Setup fixture to provide authentication headers.
    Ensures traceability (ISO/IEC/IEEE 29148) and enforcement of access control (OWASP ASVS V5).
    """
    assert BEARER_TOKEN and BEARER_TOKEN != '<REPLACE_WITH_TOKEN>', "Bearer token must be provided via environment variable."
    return {
        'Authorization': f'Bearer {BEARER_TOKEN}',
        'Content-Type': 'application/json'
    }
\****************(scope="function")
def unique_agent_data():
    """
    Creates a unique agent slug per test, adheres to test isolation (OWASP ASVS V5) and traceability (ISO/IEC/IEEE 29148).
    """
    slug = f"agent-{uuid.uuid4().hex[:8]}"
    return {
        "slug": slug,
        "display_name": "Agent Eight",
        "category": "req_synthesizer",
        "parent_id": None  # Explicitly set to null (RFC 8259 compliance)
    }
\******************('regression', 'sanity')\*************.owasp_asvs('V5')\*************.iso_29148('TC-POST-7f2b9c6b-008')
def test_create_agent_with_null_parent_id(auth_headers, unique_agent_data):
    """
    Test Case ID: TC-POST-7f2b9c6b-008
    Description: Validate agent creation with parent_id explicitly set to null.
    Standards:
      - {}\n      - {}\n      - {}
    """.format(declare_rfc_8259, declare_owasp_asvs_v5, declare_iso_29148)
    
    endpoint = f"{BASE_URL}/api/agents/"
    payload = unique_agent_data
    
    # Step: Send POST request (RFC 8259 compliance: serialize as JSON)
    response = requests.post(
        endpoint,
        json=payload,
        headers=auth_headers,
        timeout=10
    )

    # Validation: Status 200
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"

    # Validation: Response body must be valid JSON (RFC 8259)
    try:
        resp_json = response.json()
    except Exception as e:
        pytest.fail(f"Response is not valid JSON: {e}\nBody: {response.text}")

    # Validation: agent details returned
    for key in ["slug", "display_name", "category", "parent_id"]:
        assert key in resp_json, f"Missing '{key}' in response body"
        
    # Validation: Fields match the request, parent_id is explicitly null (None in Python)
    assert resp_json["slug"] == payload["slug"], "Slug mismatch in response."
    assert resp_json["display_name"] == payload["display_name"], "Display name mismatch."
    assert resp_json["category"] == payload["category"], "Category mismatch."
    assert resp_json["parent_id"] is None, "parent_id should be null in response."

    # Compliance: Ensure response does not leak sensitive information (OWASP ASVS V5)
    forbidden_attrs = set(["password", "token", "secret"])
    assert not (forbidden_attrs & resp_json.keys()), f"Sensitive attribute(s) found in response: {forbidden_attrs & resp_json.keys()}"

    # Traceability: All assertions reference test case ID TC-POST-7f2b9c6b-008 (ISO/IEC/IEEE 29148)

# No teardown required as there is no persistent resource cleanup specified; add here if system supports deletion.