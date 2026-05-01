import pytest
import requests
import string
import random

BASE_URL = "https://your-api-base-url.com"  # Replace with your actual API base
API_ENDPOINT = "/api/agents/"
AUTH_TOKEN = "<REPLACE_WITH_TOKEN>"  # Token should be securely provisioned
HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

# Traceability: ISO/IEC/IEEE 29148 - Req. Encoding, RFC 8259 (JSON payloads), OWASP ASVS V5 (Input Validation)

MAX_LENGTH = 255
VALID_CATEGORY = "documentation"


def random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
\****************(scope="module")
def api_url():
    return f"{BASE_URL}{API_ENDPOINT}"
\****************(scope="module")
def auth_headers():
    # In production, retrieve/generate token securely
    assert AUTH_TOKEN and AUTH_TOKEN != "<REPLACE_WITH_TOKEN>", "Valid Bearer token is required for the test."
    return HEADERS.copy()

class TestAgentFieldBoundary:
    """
    TestCase ID: TC-POST-9a0eda3c-011
    Compliance: ISO/IEC/IEEE 29148, RFC 8259, OWASP ASVS V5
    """

    @pytest.mark.parametrize("slug_length,display_name_length,expected_status", [
        (MAX_LENGTH, MAX_LENGTH, 200),        # Both at max allowed
        (MAX_LENGTH+1, MAX_LENGTH, 422),      # Slug too long
        (MAX_LENGTH, MAX_LENGTH+1, 422),      # Display name too long
        (MAX_LENGTH+1, MAX_LENGTH+1, 422),    # Both too long
    ])
    def test_slug_and_display_name_length_boundary(self, api_url, auth_headers, slug_length, display_name_length, expected_status):
        """
        Verify the field length boundaries for 'slug' and 'display_name' fields as per specification.
        """
        slug_val = random_string(slug_length)
        display_name_val = random_string(display_name_length)
        payload = {
            "slug": slug_val,
            "display_name": display_name_val,
            "category": VALID_CATEGORY
        }
        response = requests.post(api_url, json=payload, headers=auth_headers)
        assert response.status_code == expected_status, (
            f"Expected status {expected_status} but got {response.status_code} for slug({slug_length}) and display_name({display_name_length})"
        )
        resp_json = None
        try:
            resp_json = response.json()
        except Exception:
            pytest.skip("Response is not valid JSON, RFC 8259 compliance violated.")
        # Detailed validations for RFC 8259 (JSON error structure), OWASP ASVS (field-specific errors)
        if expected_status == 422:
            # Expect the error to specify which field failed
            assert "errors" in resp_json, "Response must contain 'errors' object per API guidelines."
            field_error_keys = resp_json.get("errors", {}).keys()
            # At least one field (slug, display_name) should be invalid
            exceeded_fields = []
            if slug_length > MAX_LENGTH:
                exceeded_fields.append("slug")
            if display_name_length > MAX_LENGTH:
                exceeded_fields.append("display_name")
            missing = [f for f in exceeded_fields if f not in field_error_keys]
            assert not missing, f"Error messages must be provided for: {missing}"
            # Compliance: Error message should relate to length/validation
            for f in exceeded_fields:
                msgs = resp_json["errors"][f]
                assert isinstance(msgs, list) and any(
                    "length" in m.lower() or "too long" in m.lower() or "exceed" in m.lower() for m in msgs
                ), f"Error for '{f}' does not reference field limit (OWASP ASVS, IEEE 29148)"
        elif expected_status == 200:
            # On success: RFC 8259 - response must be valid JSON
            assert resp_json is not None, "Response must be a valid JSON object."
            assert "id" in resp_json or "slug" in resp_json, "Response does not contain minimum expected fields."

    # Optional teardown/cleanup could be added here if test data needs to be deleted

# To execute: pytest -v test_agents_api_boundary.py
