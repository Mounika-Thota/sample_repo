import pytest
import requests

BASE_URL = "https://api.example.com"  # Replace with actual base URL
def get_existing_agent_id():
    """
    Helper to retrieve an existing agent_id. Must be implemented or replaced
    with actual fixture/data lookup in real test suites.
    """
    # Placeholder for compliance with ISO/IEC/IEEE 29148 traceability
    raise NotImplementedError("Replace with logic to obtain a valid agent_id as per preconditions.")

@pytest.fixture(scope="function")
def agent_id():
    # Precondition: Agent with <REPLACE_WITH_AGENT_ID> exists
    # Ensure API is reachable and agent exists
    # For traceability (ISO/IEC/IEEE 29148), explicitly document precondition management
    return get_existing_agent_id()

@pytest.fixture(scope="function")
def api_reachable():
    # Precondition: API is reachable
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
    except Exception as e:
        pytest.skip(f"API not reachable: {str(e)}")

@pytest.mark.security
@pytest.mark.regression
@pytest.mark.owasp_asvs("V2")
@pytest.mark.risk_level("high")
def test_put_agents_agent_id_no_auth_header(api_reachable, agent_id):
    """
    Testcase: TC-PUT-55cdd53a-005
    Validate the endpoint returns 401 Unauthorized when no Authorization header is sent.
    Compliance: RFC 8259 (JSON), OWASP ASVS V2 (Authentication), ISO/IEC/IEEE 29148 (Requirements traceability)
    """
    url = f"{BASE_URL}/api/agents/{agent_id}"
    payload = {"slug": "slug"}  # Example body parameter; nullable as per OpenAPI
    headers = {"Content-Type": "application/json"}
    # Step: Send PUT request with no Authorization header
    response = requests.put(url, headers=headers, json=payload)

    # Check RFC 8259 compliance: response must be valid JSON if an error body is returned
    if response.content:
        try:
            response.json()
        except ValueError:
            pytest.fail("Response body is not RFC 8259 compliant JSON.")

    # Validate expected outcome per OWASP ASVS V2 and test metadata
    expected_status_codes = [401]
    assert response.status_code in expected_status_codes, \
        f"Expected 401 Unauthorized, got {response.status_code}. Response: {response.text}"

    # ISO/IEC/IEEE 29148: Result is traceable and verifiable
    # Tag: security, regression; Source: openapi_spec, id: update_agent_api_agents__agent_id__put

# No teardown necessary, as this test does not alter server state or create resources.
