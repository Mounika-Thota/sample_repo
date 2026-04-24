import pytest
import requests

BASE_URL = "https://api.example.com"  # Replace with actual API base URL
ENDPOINT = "/api/agents/"
\****************(scope="function")
def bearer_token():
    """
    Fixture to retrieve a valid bearer token.
    This should be implemented securely for the target environment.
    """
    # Replace this with actual secure token retrieval logic
    # For example, reading from environment or using a secrets manager
    return "<REPLACE_WITH_TOKEN>"

def test_post_agents_empty_body_returns_422(bearer_token):
    """
    TC-POST-7f2b9c6b-019: Validate error response when request body is empty.
    Compliance:
        - RFC 8259: Ensures proper JSON handling and content-type.
        - OWASP ASVS V5, V10: Validates input, error responses, and security headers.
        - ISO/IEC/IEEE 29148: Requirements are explicit, traceable, and verifiable.
    """
    url = f"{BASE_URL}{ENDPOINT}"
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    empty_json_body = {}
    response = requests.post(url, headers=headers, json=empty_json_body)

    # Validate status code is 422 Unprocessable Entity as per specification
    assert response.status_code == 422, (
        f"Expected status 422 but got {response.status_code}. Response: {response.text}"
    )

    # Check content-type and basic compliance (RFC 8259 for JSON)
    assert response.headers.get("Content-Type", "").startswith("application/json"), (
        "Response content-type must be application/json."
    )

    # Response body schema compliance
    try:
        resp_json = response.json()
    except ValueError as exc:
        pytest.fail(f"Response is not valid JSON (RFC 8259): {exc}")

    assert "detail" in resp_json, "Response JSON must contain 'detail' key."
    details = resp_json["detail"]
    assert isinstance(details, list), "'detail' must be a list."
    assert len(details) > 0, "'detail' list should not be empty for error response."

    # According to OpenAPI schema
    for err in details:
        assert isinstance(err, dict), "Each detail must be a dict/object."
        # Traceability for each validation error per ASVS & schema
        for required_key in ["loc", "msg", "type"]:
            assert required_key in err, (
                f"Validation error objects must contain '{required_key}'."
            )
    # Verifiability: ensure at least one error pertains to missing required fields
    assert any(
        "required" in err["type"] or "missing" in err["msg"].lower()
        for err in details
    ), "At least one validation error must indicate missing required fields."
