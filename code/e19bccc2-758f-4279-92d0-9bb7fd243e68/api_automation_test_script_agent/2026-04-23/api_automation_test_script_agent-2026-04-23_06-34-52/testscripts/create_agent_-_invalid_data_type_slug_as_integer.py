import pytest
import requests

# Constants for the API
API_BASE_URL = "https://your-api-domain.com"
ENDPOINT = "/api/agents/"
\****************(scope="session")
def bearer_token():
    # Secure token retrieval mechanism, as per ISO/IEC/IEEE 29148 traceability
    # Replace with your actual implementation or mocking as needed
    return "<REPLACE_WITH_TOKEN>"
\****************(scope="class")
def api_url():
    return f"{API_BASE_URL}{ENDPOINT}"

class TestPostAgentSlugType:
    """Traceable to OWASP ASVS V5 (Validation) and V10 (Error Reporting), ISO/IEC/IEEE 29148 for requirements traceability."""

    def test_post_agent_slug_integer_invalid(self, bearer_token, api_url):
        headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "slug": 12345,  # Intentional type violation (int, RFC 8259 compliant)
            "display_name": "Agent Six",
            "category": "deployment"
        }
        response = requests.post(api_url, json=payload, headers=headers)

        # RFC 8259: Ensure the request is valid JSON, but the value is intentionally wrong type
        # ISO/IEC/IEEE 29148: Validation of negative condition, traceable test outcome
        assert response.status_code == 422, "Expected HTTP 422 for type validation error (OWASP ASVS V5, V10)"

        try:
            resp_json = response.json()
        except Exception as e:
            pytest.fail(f"Response is not valid JSON as per RFC 8259: {e}")

        # OWASP ASVS V10: Error detail structure must be present
        assert "detail" in resp_json, "Response must contain 'detail' for error reporting (OWASP ASVS V10)"
        assert isinstance(resp_json["detail"], list), "'detail' must be a list as per response schema (RFC 8259)"

        # Find validation error related to 'slug' field
        slug_error_found = False
        for err in resp_json["detail"]:
            # Per RFC 8259, ensure structure and types
            assert isinstance(err, dict), "Each error in 'detail' must be a dict (RFC 8259)"
            assert "loc" in err and "msg" in err and "type" in err, "Error dict must contain 'loc', 'msg', 'type' (ISO/IEC/IEEE 29148 traceability)"
            # Type validation error for slug: should reference 'slug' and type issue
            if "slug" in err["loc"] and "type" in err["msg"].lower():
                slug_error_found = True
                break
        assert slug_error_found, "Validation error for 'slug' type must be reported (OWASP ASVS V5, traceable negative test)"

    @pytest.fixture(scope="class", autouse=True)
    def cleanup(self):
        # No data cleanup needed since this is a negative test,
        # but fixture provided for ISO/IEC/IEEE 29148 traceability.
        yield

# To execute:
# > pytest -v test_post_agent_slug_type.py
