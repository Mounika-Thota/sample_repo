import pytest
import requests
from jsonschema import validate

# Standards Traceability:
# - ISO/IEC/IEEE 29148: Each requirement (TC-POST-9a0eda3c-004) traceable via test metadata.
# - RFC 8259: All JSON interactions follow strict JSON format.
# - OWASP ASVS: ASVS V5 (Authentication, Input Validation), V10 (Error Handling).
\****************(scope="module")
def api_base_url():
    # Ideally parametrize for different environments; ensure compliance traceability
    return "https://api.example.com"
\****************(scope="module")
def valid_token():
    # Replace this with secure token acquisition logic (for compliance, never hardcode sensitive tokens)
    # Assert token structure for RFC 8259 (JSON), and ASVS (secure token handling)
    return "<REPLACE_WITH_TOKEN>"

def test_post_agents_without_category(api_base_url, valid_token):
    """
    Test Case ID: TC-POST-9a0eda3c-004
    Description: Ensure that omitting 'category' from the request payload results in a 422 error.
    Compliance: ISO/IEC/IEEE 29148 (requirements traceability), RFC 8259, OWASP ASVS V5, V10
    """
    endpoint = "/api/agents/"
    url = f"{api_base_url}{endpoint}"

    headers = {
        "Authorization": f"Bearer {valid_token}",
        "Content-Type": "application/json"
    }
    # Send minimal valid payload omitting 'category', ensuring standards compliance (input validation, error handling)
    payload = {
        "slug": "agent123",  # must be non-empty per spec
        "display_name": "Agent 123"  # must be non-empty per spec
    }

    response = requests.post(url, headers=headers, json=payload)

    # Trace step: Status 422 returned
    assert response.status_code == 422, (
        f"Expected status code 422, got {response.status_code} - "
        f"Response: {response.text}"
    )

    # ISO/IEC/IEEE 29148 — Validate response verifiably against schema
    # RFC 8259 — Ensure returned JSON is valid
    try:
        resp_json = response.json()
    except ValueError:
        pytest.fail("Response is not valid JSON (RFC 8259): %s" % response.text)

    # OWASP ASVS V10 — Error should not leak sensitive info, only describe missing field
    expected_schema = {
        "type": "object",
        "properties": {
            "detail": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "loc": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 2,
                            "maxItems": 2
                        },
                        "msg": {"type": "string"},
                        "type": {"type": "string"}
                    },
                    "required": ["loc", "msg", "type"]
                }
            }
        },
        "required": ["detail"]
    }
    validate(instance=resp_json, schema=expected_schema)

    # Find missing category error
    missing_category_found = any(
        error.get("loc") == ["body", "category"] and
        error.get("msg") == "field required" and
        error.get("type") == "value_error.missing"
        for error in resp_json.get("detail", [])
    )
    assert missing_category_found, (
        "Response details must indicate missing 'category' field as required: "
        f"{resp_json}"
    )

    # Compliance checks
    # - All assertions are traceable/verifiable (ISO/IEC/IEEE 29148)
    # - Proper JSON handling (RFC 8259)
    # - Proper error output (OWASP ASVS V10, V5)

# No teardown necessary - POST does not create resource due to 422
