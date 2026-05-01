import os
import pytest
import requests

BASE_URL = os.getenv("API_BASE_URL", "https://api.example.com")  # Should be set in environment
BEARER_TOKEN = os.getenv("API_BEARER_TOKEN", "<REPLACE_WITH_TOKEN>")  # Must be set externally for compliance: never hardcode secrets
\****************(scope="module")
def auth_headers():
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    return headers
\************************\********************\*************.owasp_asvs("V5")
def test_post_agent_slug_type_error(auth_headers):
    """
    TC-POST-9a0eda3c-006:
    Validate error response if a required field is of wrong type (e.g., integer for slug).
    
    Traceability:
      - ISO/IEC/IEEE 29148:Requirements Validation
      - RFC 8259: JSON strict typing
      - OWASP ASVS V5: Data Validation requirements
    """
    # Arrange
    endpoint = f"{BASE_URL}/api/agents/"
    payload = {
        "slug": 123456,  # Should be string, sending integer per test case
        "display_name": "Malformed Agent",
        "category": "api_doc_testing"
    }

    # Act
    response = requests.post(endpoint, headers=auth_headers, json=payload)

    # Assert
    assert response.status_code == 422, (
        f"Expected status 422 Unprocessable Entity, got {response.status_code}"
    )

    # ISO/IEC/IEEE 29148: Schema validation; RFC8259: Validate error format
    try:
        body = response.json()
    except Exception as e:
        pytest.fail(f"Response is not valid JSON: {e}")
    assert "detail" in body, "Response must contain 'detail' field per API spec."
    # Find slug type error in details
    slug_error = next((err for err in body["detail"] if err.get("loc") == ["body", "slug"]), None)
    assert slug_error is not None, "'detail' field must contain an error for 'slug'."
    assert slug_error.get("msg") == "str type expected", (
        f"Expected error message 'str type expected', got '{slug_error.get('msg')}'"
    )
    assert slug_error.get("type") == "type_error.str", (
        f"Expected error type 'type_error.str', got '{slug_error.get('type')}'"
    )
# No teardown needed (no data created)
