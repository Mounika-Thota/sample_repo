import pytest
import requests

BASE_URL = "https://api.example.com"  # Should be parameterized/environment variable
ENDPOINT = "/api/agents/"
\****************(scope="module")
def bearer_token():
    # Token should be securely obtained (not hardcoded). Placeholder for real token retrieval logic.
    # For standards compliance (OWASP ASVS V5/V10), ensure secure storage and retrieval.
    return "<REPLACE_WITH_TOKEN>"
\****************(scope="function")
def cleanup():
    # If any resources could be created, implement teardown logic here.
    yield
    # No teardown required for invalid payload test (since creation shouldn't occur).
\**********************\************************\*************************(
    "slug, display_name, category",
    [
        ("'; DROP TABLE agents; --", "'; DROP TABLE users; --", "testing"),
    ]
)
def test_sql_injection_input_sanitization(bearer_token, cleanup, slug, display_name, category):
    """Validate input sanitization by sending SQL injection payload in slug and display_name fields.
    Standards: RFC 8259 (JSON format), OWASP ASVS V5 (input validation), V10 (error handling), ISO/IEC/IEEE 29148 (requirements traceability).
    """
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "slug": slug,
        "display_name": display_name,
        "category": category
    }

    response = requests.post(
        f"{BASE_URL}{ENDPOINT}",
        json=payload,
        headers=headers
    )

    # ISO/IEC/IEEE 29148: Requirements are traceable to:
    #   - Return 400 or 422 with validation error if malicious input detected (OWASP ASVS V5)
    assert response.status_code in [400, 422], (
        f"Expected 400 or 422, got {response.status_code}. Response body: {response.text}"
    )

    try:
        resp_json = response.json()
        # RFC 8259: Ensure JSON response
    except ValueError:
        pytest.fail("Response is not valid JSON. RFC 8259 compliance breached.")

    assert "detail" in resp_json, (
        "Response JSON must contain 'detail' key as per expected error schema. OWASP ASVS V10 compliance."
    )
    assert isinstance(resp_json["detail"], list), (
        "'detail' must be a list as per expected schema."
    )
    for error_item in resp_json["detail"]:
        assert "loc" in error_item and "msg" in error_item and "type" in error_item, (
            "Each error detail must have 'loc', 'msg', and 'type' fields. Ensures RFC 8259, ASVS error reporting."
        )
    # Verification traceability for ISO/IEC/IEEE 29148: "Status code", "error details", "message content".

    # Optional: Validate that the input was not simply echoed back unsanitized
    if slug in str(resp_json):
        pytest.fail("Malicious slug was reflected in response. Input not properly sanitized. OWASP ASVS V5 compliance failed.")
    if display_name in str(resp_json):
        pytest.fail("Malicious display_name was reflected in response. Input not properly sanitized. OWASP ASVS V5 compliance failed.")
