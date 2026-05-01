import pytest
import requests

def get_bearer_token():
    """
    Placeholder for secure retrieval of a valid Bearer token.
    Implement actual logic to fetch the token as per your environment.
    """
    # Example: return os.environ["API_BEARER_TOKEN"]
    raise NotImplementedError("Replace with secure token retrieval implementation.")
\****************(scope="module")
def api_base_url():
    # Specify your API base URL, for example via env variable or testconfig
    return "https://api.example.com"
\****************(scope="module")
def valid_token():
    # Retrieve a valid Bearer token
    return get_bearer_token()

def build_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def test_missing_slug_returns_422(api_base_url, valid_token):
    """
    TC-POST-9a0eda3c-002: Verify the API returns a 422 error when the required 'slug' field is missing from the payload.
    Standards: ISO/IEC/IEEE 29148, RFC 8259, OWASP ASVS V5 & V10
    """
    endpoint = "/api/agents/"
    url = api_base_url + endpoint
    payload = {
        "display_name": "Pytest Agent",  # required and valid
        "category": "testing"            # required and valid, assuming 'testing' is allowed
        # 'slug' is intentionally omitted
    }
    headers = build_headers(valid_token)

    response = requests.post(url, json=payload, headers=headers)

    # RFC 8259 - Validate response is well-formed JSON
    try:
        response_json = response.json()
    except ValueError:
        pytest.fail("Response body is not a valid RFC 8259 JSON object.")

    # ISO/IEC/IEEE 29148: Requirements are traceable to test ID and expected behavior
    # OWASP ASVS V5 (Validation): Ensure missing required field rejected
    # OWASP ASVS V10 (Error Handling): Proper error message for validation failure
    assert response.status_code == 422, f"Expected HTTP 422, got {response.status_code}"

    assert "detail" in response_json, "'detail' key not found in response JSON."
    missing_slug_error = None
    for err in response_json["detail"]:
        if err.get("loc") == ["body", "slug"] and \
           err.get("msg") == "field required" and \
           err.get("type") == "value_error.missing":
            missing_slug_error = err
            break
    assert missing_slug_error is not None, (
        "Expected error about missing 'slug' field not found in response body. "
        "traceability: TC-POST-9a0eda3c-002, ASVS.V5, ASVS.V10"
    )