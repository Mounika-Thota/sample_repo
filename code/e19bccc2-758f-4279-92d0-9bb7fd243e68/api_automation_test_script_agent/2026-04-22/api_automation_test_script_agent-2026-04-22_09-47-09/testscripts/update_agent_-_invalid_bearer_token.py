import pytest
import requests

# Standards compliance:
# - RFC 8259: Strict JSON formatting
# - OWASP ASVS: V2 (Authentication, Session Management)
# - ISO/IEC/IEEE 29148: Requirements traceability in docstrings, explicit assertions for all outcomes

BASE_URL = "https://api.example.com"  # Replace with actual API base URL as per environment config

@pytest.fixture(scope="module")
def agent_id():
    """Setup: Ensure agent exists for test (Precondition: 'Agent with <REPLACE_WITH_AGENT_ID> exists')
    Returns agent id for use in test.
    Requirements traceability: ISO/IEC/IEEE 29148"""
    # This fixture should be replaced with a mechanism to fetch/create a real agent Id
    # For traceability, do not use hardcoded value; fetch from environment or setup API
    # Example:
    # response = requests.post(f"{BASE_URL}/api/agents", headers={"Authorization": "Bearer <valid-token>", "Content-Type": "application/json"}, json={"slug": "setup-agent"})
    # assert response.status_code in [200, 201]
    # return response.json()["id"]
    # For this template, raise NotImplementedError
    raise NotImplementedError("Fetch/create agent_id as per environment setup.")

@pytest.mark.security
@pytest.mark.regression
@pytest.mark.owasp_asvs("V2")
def test_put_agent_unauthorized(agent_id):
    """
    Test ID: TC-PUT-55cdd53a-004
    Description: Validate that update is rejected with 401 Unauthorized when Bearer token is invalid.
    Compliance: RFC 8259 (JSON), OWASP ASVS V2, ISO/IEC/IEEE 29148 (Traceable requirements)
    Preconditions:
      - API is reachable
      - Agent with <REPLACE_WITH_AGENT_ID> exists
    Steps:
      - Send PUT request to /api/agents/<agent_id> with invalid Authorization header and valid body.
    Expected Results:
      - Status 401 or error response as per framework
    Tags: security, regression
    OWASP ASVS Ref: V2
    Risk Level: High
    """
    endpoint = f"{BASE_URL}/api/agents/{agent_id}"
    headers = {
        "Authorization": "Bearer invalid-token",  # Per test case
        "Content-Type": "application/json"
    }
    # Minimal valid body, respecting RFC 8259 and test metadata
    payload = {"slug": "slug"}  # 'slug' is optional and nullable, but sending valid value for spec compliance

    response = requests.put(endpoint, headers=headers, json=payload)

    # ISO/IEC/IEEE 29148: Each requirement verified by explicit assertion
    assert response.status_code == 401, (
        f"Expected 401 Unauthorized per OWASP ASVS V2.\n"
        f"Actual status code: {response.status_code}\nResponse body: {response.text}"
    )
    # RFC 8259: Response body must be valid JSON if API spec mandates
    try:
        resp_json = response.json()
    except ValueError:
        resp_json = None
    assert resp_json is not None or response.text.strip() == '', "Response should be valid JSON or empty as per RFC 8259."

    # OWASP ASVS V2: Error message should not leak sensitive info
    if resp_json:
        assert 'error' in resp_json or 'message' in resp_json, (
            "Expected standard error structure (error/message) per API framework and OWASP ASVS."
        )
        # Optionally, check that sensitive data is not exposed
        for key in ('token', 'password', 'credential'):
            values = [resp_json.get('error', ''), resp_json.get('message', '')]
            assert not any(key in val.lower() for val in values), "Sensitive info leakage detected in error message."

# Teardown (if needed): No agent update occurs due to test case (unauthorized), so no cleanup needed