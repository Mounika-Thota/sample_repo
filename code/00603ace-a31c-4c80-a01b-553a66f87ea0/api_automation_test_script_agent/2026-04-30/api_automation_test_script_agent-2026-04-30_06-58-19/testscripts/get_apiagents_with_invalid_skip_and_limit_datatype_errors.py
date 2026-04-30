import pytest
import requests
from typing import Dict

API_BASE_URL = "https://api.example.com"  # Replace with actual API base URL
def get_bearer_token() -> str:
    # Implement token retrieval logic here, or fetch from env/config
    # For compliance: sensitive values must not be hard-coded
    # ISO/IEC/IEEE 29148: requirements traceability implemented via explicit config
    return "<REPLACE_WITH_TOKEN>"
\****************(scope="module")
def auth_header() -> Dict[str, str]:
    token = get_bearer_token()
    assert token and token != "<REPLACE_WITH_TOKEN>", "Bearer token must be configured for test execution."
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
\*************************("query,invalid_param,expected_error", [
    ({"skip": "abc", "limit": 20}, "skip", "value is not a valid integer"),
    ({"skip": 10, "limit": -1}, "limit", "ensure this value is greater than or equal to 0"),
    ({"skip": 1.5, "limit": 10}, "skip", "value is not a valid integer")
])
def test_get_agents_invalid_skip_limit(auth_header, query, invalid_param, expected_error):
    """Validate GET /api/agents/ returns 422 for invalid skip and limit (OWASP ASVS V5, V10, ISO/IEC/IEEE 29148)"""
    # Step 1: Send GET request with invalid parameter
    url = f"{API_BASE_URL}/api/agents/"
    resp = requests.get(url, headers=auth_header, params=query)

    # Assert 422 Unprocessable Entity (RFC 9110, RFC 8259 compliance)
    assert resp.status_code == 422, f"Expected status 422, got {resp.status_code}. Trace: TC-GET-feb8d5e2-03"

    # Assert response content type JSON
    content_type = resp.headers.get("Content-Type", "")
    assert "application/json" in content_type, f"Expected application/json, got {content_type}. Standard: RFC 8259"

    # Assert response conforms to expected error schema (partial schema due to variability)
    try:
        error_body = resp.json()
    except Exception as exc:
        pytest.fail(f"Response not in JSON format: {exc}")
    
    # Compliance: All error details must be traceable
    assert "detail" in error_body, "Missing 'detail' in error body. OWASP ASVS V10"
    detail_list = error_body["detail"]
    assert isinstance(detail_list, list) and detail_list, "'detail' must be a non-empty list."
    found = False
    for err in detail_list:
        if (
            isinstance(err, dict)
            and err.get("loc")
            and invalid_param in err["loc"]
            and expected_error in err.get("msg", "")
        ):
            # Negative test passes if invalid param triggers correct validation
            found = True
            # Standard: ISO 29148 - requirement for traceability to input parameter
            break
    assert found, f"Expected validation error for '{invalid_param}' with message '{expected_error}' in {detail_list}"

# OWASP ASVS V5: Validation, V10: Error handling & injection protection
# ISO/IEC/IEEE 29148: Requirements are traceable via test id: TC-GET-feb8d5e2-03
# RFC 8259: JSON structure compliance
#
# To execute:
# pytest -v test_get_agents_invalid_parameters.py
