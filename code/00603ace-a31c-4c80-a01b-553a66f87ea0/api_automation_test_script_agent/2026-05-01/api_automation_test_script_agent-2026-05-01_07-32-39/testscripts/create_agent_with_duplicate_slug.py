import pytest
import requests

BASE_URL = "https://api.example.com"  # Replace with actual base URL
AGENT_ENDPOINT = "/api/agents/"
SLUG = "duplicate-agent"
DISPLAY_NAME = "Duplicate Agent"
CATEGORY = "testing"
HEADERS = {
    "Authorization": "Bearer <REPLACE_WITH_TOKEN>",  # Token to be injected securely
    "Content-Type": "application/json"
}

def create_agent(slug, display_name, category, headers=HEADERS):
    payload = {
        "slug": slug,
        "display_name": display_name,
        "category": category
    }
    response = requests.post(
        BASE_URL + AGENT_ENDPOINT,
        json=payload,
        headers=headers
    )
    return response
\****************(scope="module")
def ensure_preexisting_duplicate_agent():
    """
    Ensures that an agent with the slug already exists to validate uniqueness logic.
    Precondition step required by test ISO/IEC/IEEE 29148 and OWASP ASVS.
    """
    # Ensure idempotency: attempt to create the agent, ignore errors if it already exists
    response = create_agent(SLUG, DISPLAY_NAME, CATEGORY)
    yield
    # Teardown/cleanup step can be implemented here if API supports delete
    # e.g., requests.delete(BASE_URL + AGENT_ENDPOINT + SLUG, headers=HEADERS)
\************************\*************.owasp_asvs("V5")
def test_duplicate_agent_slug_uniqueness_violation(ensure_preexisting_duplicate_agent):
    """
    Testcase TC-POST-9a0eda3c-007: Validate that attempting to create an agent with an existing slug returns an appropriate error or prevents duplicate records.
    Fulfills requirements for RFC 8259 (JSON structure), ISO/IEC/IEEE 29148 (test traceability), OWASP ASVS V5 (Validation of uniqueness for critical data).
    """
    response = create_agent(SLUG, DISPLAY_NAME, CATEGORY)

    # Assert appropriate status code per OpenAPI, RFC 8259, and negative test expectations
    assert response.status_code == 422, f"Expected status code 422, got {response.status_code}"
    # Assert response is valid JSON
    try:
        response_json = response.json()
    except Exception as exc:
        pytest.fail(f"Response body is not valid JSON: {exc}")
    
    # Validate uniqueness violation is clearly reported
    assert "detail" in response_json, "Response JSON should contain 'detail' key as per RFC 8259."
    # 'detail' should be a list containing a dict with the expected message
    details = response_json["detail"]
    assert isinstance(details, list), f"'detail' should be a list, got {type(details)}"
    found = any(item.get("msg", "").lower().find("unique") != -1 and slug in item.get("msg", "") for item in details for slug in [SLUG])
    assert found, f"Expected a detail entry indicating uniqueness violation for slug '{SLUG}'"
