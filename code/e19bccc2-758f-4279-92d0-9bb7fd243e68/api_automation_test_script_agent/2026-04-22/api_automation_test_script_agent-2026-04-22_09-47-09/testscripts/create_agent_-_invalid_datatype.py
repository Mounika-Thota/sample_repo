import pytest
import requests

API_BASE_URL = "https://api.example.com"  # Replace with actual base URL
ENDPOINT = "/api/agents/"
AUTH_TOKEN = "<REPLACE_WITH_TOKEN>"  # Must be set to a valid token prior to execution

@pytest.fixture(scope="module")
def auth_headers():
    """
    Fixture to provide authentication headers compliant with RFC 8259 and OWASP ASVS for secure authentication transport.
    """
    return {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }

def build_invalid_payload(slug_value, display_name_value, category_value):
    """
    Build the invalid payload with improper types for testing validation according to ISO/IEC/IEEE 29148 (requirements traceability).
    """
    return {
        "slug": slug_value,               # Invalid: should be string
        "display_name": display_name_value,      # Invalid: should be string
        "category": category_value        # Valid
    }

def assert_validation_error_response(response_json, invalid_fields):
    """
    Assert the structure of validation errors (RFC 8259, ISO/IEC/IEEE 29148: Requirement 6.7.1.3).
    """
    assert "detail" in response_json, "Response must contain 'detail' field for validation errors."
    for field in invalid_fields:
        found = any(any(str(loc_item) == field for loc_item in err.get("loc", [])) and err.get("type") for err in response_json["detail"])
        assert found, f"Validation error for '{field}' must be present and include 'type'."
        # Compliance: Include specific error messages for invalid data types.

@pytest.mark.owasp_asvs(["V5", "V10"])
@pytest.mark.regression
@pytest.mark.risk_level("medium")
def test_post_agents_invalid_types_slug_and_display_name(auth_headers):
    """
    Validate POST /api/agents/ fails with 422 when required fields have invalid types per RFC 8259, OWASP ASVS, ISO/IEC/IEEE 29148.
    """
    # Preconditions
    # - API is reachable (implicit via HTTP request)
    # - Valid Bearer token available
    
    # Step 1: Send invalid payload (slug as integer)
    payload = build_invalid_payload(slug_value=12345, display_name_value="Valid Name", category_value="testing")
    response = requests.post(
        API_BASE_URL + ENDPOINT,
        headers=auth_headers,
        json=payload
    )
    assert response.status_code == 422, f"Expected status code 422 for slug type error, got {response.status_code}"
    assert_validation_error_response(response.json(), invalid_fields=["slug"])

    # Step 2: Send invalid payload (display_name as integer)
    payload = build_invalid_payload(slug_value="valid-slug", display_name_value=67890, category_value="testing")
    response = requests.post(
        API_BASE_URL + ENDPOINT,
        headers=auth_headers,
        json=payload
    )
    assert response.status_code == 422, f"Expected status code 422 for display_name type error, got {response.status_code}"
    assert_validation_error_response(response.json(), invalid_fields=["display_name"])

    # Step 3: Send payload with both as integers
    payload = build_invalid_payload(slug_value=12345, display_name_value=67890, category_value="testing")
    response = requests.post(
        API_BASE_URL + ENDPOINT,
        headers=auth_headers,
        json=payload
    )
    assert response.status_code == 422, f"Expected status code 422 for both fields type error, got {response.status_code}"
    assert_validation_error_response(response.json(), invalid_fields=["slug", "display_name"])
