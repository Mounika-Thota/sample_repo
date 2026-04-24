import pytest
import requests
import string
import random

# Constants (these should be configurable or fetched from a config file/environment)
BASE_URL = "https://api.example.com"  # Replace with actual base URL
MAX_SLUG_LENGTH = 64  # Example: Should be set according to openapi spec / documentation
MAX_DISPLAY_NAME_LENGTH = 128  # Example: Should be set according to openapi spec / documentation
CATEGORY_ENUM = ["testing"]  # Example enum values. These should match actual API spec.

def random_string(length):
    """Generate a random string of ASCII letters and digits, compliant with RFC 8259 (JSON)."""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=length))
\****************(scope="module")
def bearer_token():
    # Placeholder for token retrieval logic
    # Must be replaced with secure token acquisition compliant with ASVS authentication requirements
    return "<REPLACE_WITH_TOKEN>"
\****************(scope="module")
def cleanup_agent():
    created_agent_ids = []
    yield created_agent_ids
    # Teardown: Delete created agents
    for agent_id in created_agent_ids:
        headers = {"Authorization": f"Bearer <REPLACE_WITH_TOKEN>"}
        requests.delete(f"{BASE_URL}/api/agents/{agent_id}", headers=headers)
\************************\**********************\******************("V5")
def test_agent_creation_max_length_fields(bearer_token, cleanup_agent):
    # Construct request payload with maximum allowed lengths
    slug = random_string(MAX_SLUG_LENGTH)
    display_name = random_string(MAX_DISPLAY_NAME_LENGTH)
    category = CATEGORY_ENUM[0]  # Since examples specify 'testing'

    payload = {
        "slug": slug,
        "display_name": display_name,
        "category": category
    }

    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }

    # Precondition: API Reachability (ASVS V5)
    health_response = requests.get(f"{BASE_URL}/api/agents/", headers=headers)
    assert health_response.status_code in [200, 401, 403], "API not reachable (RFC 8259 compliance)"

    # Step: Send POST request to create agent with boundary values
    response = requests.post(f"{BASE_URL}/api/agents/", json=payload, headers=headers)
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code} (ASVS V5, RFC 8259)"

    # Validate response body structure (ISO/IEC/IEEE 29148 traceable requirement)
    resp_json = response.json()
    assert isinstance(resp_json, dict), "Response must be a JSON object (RFC 8259)"

    # Traceability & Verifiability checks
    assert 'slug' in resp_json, "Missing 'slug' in response (ISO/IEC/IEEE 29148: requirement traceability)"
    assert 'display_name' in resp_json, "Missing 'display_name' in response"
    assert resp_json['slug'] == slug, f"Response slug does not match sent value: {slug}"
    assert resp_json['display_name'] == display_name, f"Response display_name does not match sent value: {display_name}"
    assert resp_json['category'] == category, f"Response category does not match sent value: {category}"

    # Ensure max length fields are echoed back (boundary test)
    assert len(resp_json['slug']) == MAX_SLUG_LENGTH, "Response slug length does not match maximum length"
    assert len(resp_json['display_name']) == MAX_DISPLAY_NAME_LENGTH, "Response display_name length does not match maximum length"

    # For compliance, record created agent for cleanup
    if 'id' in resp_json:
        cleanup_agent.append(resp_json['id'])

# Test traceability: Each assertion corresponds to OWASP ASVS V5 (API input validation, response integrity),
# RFC 8259 (strict JSON compliance), ISO/IEC/IEEE 29148 (requirements traceability & verifiability).
