import os
import requests
import pytest

# Constants - replace BASE_URL with actual API base URL as appropriate
BASE_URL = os.environ.get("API_BASE_URL", "https://api.example.com")  # Should be configurable per environment
ENDPOINT = "/api/agents/"
EXPECTED_STATUS_CODES = [415, 400]  # per test case and RFC 8259/OWASP guidance

# Standards compliance documentation:
# * RFC 8259 - Ensures request body/media type contract
# * OWASP ASVS V10 - API & web service security, error handling
# * ISO/IEC/IEEE 29148 - Requirements traceability is ensured in comments and asserts

def get_bearer_token():
    """
    Placeholder for retrieving a valid bearer token for API authentication.
    Returns:
        str: Valid bearer token
    """
    # In a real implementation, this should retrieve securely from an env variable or secret store
    token = os.environ.get("API_BEARER_TOKEN")
    if not token:
        raise RuntimeError("Bearer token not set in environment variable 'API_BEARER_TOKEN'.")
    return token
\****************(scope="module")
def auth_token():
    # Setup: obtain authentication token
    return get_bearer_token()
\****************(scope="function", autouse=True)
def setup_and_teardown():
    # Preconditions: API is reachable
    try:
        resp = requests.get(BASE_URL + "/status" or BASE_URL)  # Use a health/status endpoint if available
        assert resp.status_code < 500, "API is not reachable (see ISO/IEC/IEEE 29148 - verifiable precondition)"
    except Exception as ex:
        pytest.skip(f"API unreachable: {ex}")
    yield
    # Teardown: No cleanup required for negative test


def test_post_agents_with_unsupported_content_type(auth_token):
    """
    Testcase ID: TC-POST-7f2b9c6b-017
    Title: Validate error response when Content-Type header is not application/json.
    Standards: RFC 8259 (JSON encoding), OWASP ASVS V10 (error handling), ISO/IEC/IEEE 29148 (traceability)
    """
    url = BASE_URL + ENDPOINT
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "text/plain"
    }
    # Send empty or plain text body, since body is not specified in negative case
    data = "plain-text-data-placeholder"
    response = requests.post(url, headers=headers, data=data, timeout=15)

    # --- Standards compliance assertions ---
    # ISO/IEC/IEEE 29148: All requirements are verifiable below via assertions

    # Assert status code (should be 415 Unsupported Media Type, or 400 Bad Request as per RFC/ASVS)
    assert response.status_code in EXPECTED_STATUS_CODES, (
        f"Expected status 415 or 400, got {response.status_code}. (RFC 8259, OWASP ASVS V10)"
    )

    # Assert error message is present and refers to media type (traceable)
    try:
        resp_json = response.json()
    except Exception:
        resp_json = None

    error_msg = None
    # OWASP: Error details should be clear but not leak implementation
    if resp_json:
        # Look for common keys
        error_msg = resp_json.get("error") or resp_json.get("message") or str(resp_json)
    else:
        error_msg = response.text or ""
    assert (
        "media type" in error_msg.lower()
        or "unsupported" in error_msg.lower()
        or "content-type" in error_msg.lower()
        or "application/json" in error_msg.lower()
        or "not supported" in error_msg.lower()
    ), f"Expected error message about unsupported media type, got: {error_msg}"

    # ISO/IEC/IEEE 29148: Each requirement traceable by assertion and comment

# End of script
