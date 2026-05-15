import pytest
import requests
import json
from jsonschema import validate, ValidationError

API_BASE_URL = "https://api.example.com"  # Update as needed
AGENTS_ENDPOINT = "/api/agents/"

@pytest.fixture(scope="session")
def bearer_token():
    """Obtain a valid Bearer token. Implement actual token retrieval as per environment."""
    # Compliant with RFC 8259 and OWASP ASVS V2/V5: avoid hardcoded credentials
    # Replace with secure retrieval logic as needed
    return "REPLACE_WITH_TOKEN"

@pytest.fixture(scope="function")
def setup_agent_payload():
    """Prepare agent creation payload. Ensure RFC 8259 (JSON) and field constraints."""
    return {
        "slug": "test-agent1",              # unique, non-empty
        "display_name": "Test Agent",      # non-empty
        "category": "usg",                # enum
        "description": "Agent for testing.", # nullable
        "parent_id": None,
    }

def response_schema():
    """Response schema as per OpenAPI spec. ISO/IEC/IEEE 29148 traceability."""
    # Schema should be updated to reflect actual response; kept generic for demonstration
    return {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "slug": {"type": "string"},
            "display_name": {"type": "string"},
            "category": {"type": "string"},
            "description": {"type": ["string", "null"]},
            "parent_id": {"type": ["string", "null"]}
        },
        "required": ["id", "slug", "display_name", "category"]
    }

@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.functional
@pytest.mark.high
@pytest.mark.asvs("V2")
@pytest.mark.asvs("V5")
@pytest.mark.asvs("V10")
def test_create_agent_success(bearer_token, setup_agent_payload):
    """Test successful creation of an agent via POST /api/agents/ (RFC 8259/OWASP-ASVS/ISO/IEC/IEEE 29148)."""
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
    }
    payload = setup_agent_payload

    # Step 1: Send POST request with all required and optional fields
    response = requests.post(
        f"{API_BASE_URL}{AGENTS_ENDPOINT}",
        headers=headers,
        data=json.dumps(payload),  # RFC 8259 compliance
        timeout=15
    )

    # Validation 1: API is reachable, status code is 200
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}."

    # Validation 2: Content-Type is application/json
    content_type = response.headers.get("Content-Type", "")
    assert "application/json" in content_type, f"Expected application/json, got {content_type}."

    # Validation 3: Response body is non-empty and valid JSON (RFC 8259)
    try:
        response_json = response.json()
    except ValueError:
        pytest.fail("Response body is not valid JSON.")
    assert response_json, "Response body is empty."

    # Validation 4: Response matches OpenAPI response schema (verifiable, ISO/IEC/IEEE 29148)
    schema = response_schema()
    try:
        validate(instance=response_json, schema=schema)
    except ValidationError as err:
        pytest.fail(f"Response schema validation failed: {err.message}")

    # Traceability: Ensure all submitted fields are reflected in the response
    for field in ["slug", "display_name", "category", "description", "parent_id"]:
        if field in payload:
            assert response_json.get(field) == payload[field], f"Mismatch for field '{field}': expected {payload[field]}, got {response_json.get(field)}"

    # Compliance: OWASP ASVS V2 (Authentication), V5 (Input validation), V10 (Error handling)
    # All assertions above trace back to these security requirements.

    # Teardown: No deletion is performed as per test type. If required, implement cleanup logic here.
