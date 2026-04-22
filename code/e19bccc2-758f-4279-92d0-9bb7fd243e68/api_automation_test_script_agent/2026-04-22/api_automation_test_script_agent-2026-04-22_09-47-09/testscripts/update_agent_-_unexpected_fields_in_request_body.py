import os
import pytest
import requests

def get_bearer_token():
    """
    Retrieve a valid Bearer token from environment or secure store.
    This function assumes that ISO/IEC/IEEE 29148 requirements for config are followed.
    """
    token = os.getenv("BEARER_TOKEN")
    assert token, "Bearer token is required per preconditions. Set BEARER_TOKEN environment variable."
    return token

def get_agent_id():
    """
    Retrieve agent ID to use for the test case.
    This value should be set in the environment to promote traceability and repeatability.
    """
    agent_id = os.getenv("AGENT_ID")
    assert agent_id, "Valid agent_id is required per preconditions. Set AGENT_ID environment variable."
    return agent_id

@pytest.fixture(scope="module")
def api_base_url():
    """
    Retrieve API base URL, compliant with test environment config management.
    """
    url = os.getenv("API_BASE_URL")
    assert url, "API base URL missing. Set API_BASE_URL environment variable."
    return url.rstrip("/")

@pytest.fixture(scope="module")
def headers():
    """
    Build required headers for the request (RFC 8259, OWASP ASVS V5/V10)
    """
    return {
        "Authorization": f"Bearer {get_bearer_token()}",
        "Content-Type": "application/json"
    }

@pytest.mark.regression
@pytest.mark.owasp_asvs(["V5", "V10"])
def test_put_agent_with_extra_field(api_base_url, headers):
    """
    TC-PUT-55cdd53a-013:
    Validate that PUT /api/agents/{agent_id} with extra undefined fields is handled per RFC 8259 (ignore or reject unknowns),
    traceable to OWASP ASVS V5 (Validation), V10 (API Security),
    and ISO/IEC/IEEE 29148 (requirement traceability and verifiability).
    """
    agent_id = get_agent_id()
    url = f"{api_base_url}/api/agents/{agent_id}"
    payload = {"bogus_field": "unexpected"}  # Intentionally not in schema

    response = requests.put(url, headers=headers, json=payload)
    
    assert response.status_code in {200, 422}, (
        f"Expected status 200 or 422 per API and RFC 8259 section 7, got {response.status_code} ({response.text})"
    )
    if response.status_code == 422:
        # Verify error response schema conforms to RFC 8259 (must be valid JSON)
        try:
            data = response.json()
        except Exception as ex:
            pytest.fail(f"422 response not valid JSON (RFC 8259): {ex}")
        assert "errors" in data or "error" in data, (
            "Validation error response should follow documented error structure (ISO/IEC/IEEE 29148: verifiability)."
        )
        # Optionally: verify error details for unknown field
        found_bogus = any(
            "bogus_field" in str(detail) for detail in data.get("errors", [])
        ) or (
            "bogus_field" in str(data.get("error", ""))
        )
        assert found_bogus, "Error response should reference 'bogus_field' as an unknown or invalid property."
    elif response.status_code == 200:
        # Ensure response is valid JSON (RFC 8259), even if extra is ignored
        try:
            data = response.json()
        except Exception as ex:
            pytest.fail(f"200 response not valid JSON (RFC 8259): {ex}")
    # Requirement traceability (ISO/IEC/IEEE 29148): this test case covers
    #   - Soft-failure or success with ignored extra (RFC 8259, ASVS V10)
    #   - Strict schema validation error (ASVS V5, ISO/IEC/IEEE 29148 verifiability)

def teardown_module(module):
    """
    No resource modification expected, so no teardown necessary.
    """
    pass
