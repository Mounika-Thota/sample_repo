import pytest
import requests

BASE_URL = "https://api.example.com"  # Replace with actual base URL
\****************(scope="module")
def bearer_token():
    # Setup: Fetch or generate a valid bearer token as per auth mechanism.
    # For traceability, clearly comment location and retrieval method (ISO/IEC/IEEE 29148: requirements traceability)
    # Replace with actual token retrieval logic.
    return "<REPLACE_WITH_TOKEN>"
\****************(scope="function")
def api_url():
    # Alignment to RFC 8259: API endpoint must be a valid URL
    return f"{BASE_URL}/api/agents/"
\*************.owasp_asvs("V5", "V10")\************************\**********************
class TestCreateAgentBoundaryCases:
    def test_empty_slug_and_display_name(self, bearer_token, api_url):
        """Validate error response when slug or display_name is empty string (Compliant with RFC 8259, OWASP ASVS, ISO/IEC/IEEE 29148)."""
        # Preconditions: API reachable, valid bearer token available
        headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json"
        }
        # Step 1: Send POST with empty slug/display_name, valid category (ISO/IEC/IEEE 29148)
        payload = {
            "slug": "",
            "display_name": "",
            "category": "usg"  # per example, assuming 'usg' is valid (RFC 8259 compliance: enum constraint)
        }

        response = requests.post(api_url, headers=headers, json=payload)

        # Validation 1: Status 422 (RFC 8259 specifies proper error status response; OWASP ASVS V5 for input validation)
        assert response.status_code == 422, f"Expected 422, got {response.status_code}. Response: {response.content}"

        # Validation 2: Response body JSON format (strict RFC 8259 compliance)
        try:
            resp_json = response.json()
        except Exception:
            pytest.fail(f"Response is not valid RFC 8259 JSON: {response.text}")

        # Validation 3: 'detail' key present and conforms to schema (ISO/IEC/IEEE 29148: verifiability, OWASP ASVS V10: error messages)
        assert "detail" in resp_json, "Response missing 'detail' for validation errors."
        assert isinstance(resp_json["detail"], list), "'detail' must be a list as per expected schema."

        # Each validation error must indicate location, error message, and error type (schema compliance)
        found_slug = found_display_name = False
        for item in resp_json["detail"]:
            # RFC 8259: properties must be strings
            assert isinstance(item.get("loc"), list), "'loc' must be a list."
            assert isinstance(item.get("msg"), str), "'msg' must be a string."
            assert isinstance(item.get("type"), str), "'type' must be a string."
            # Check if validation error affects slug or display_name as empty
            if any("slug" == loc_item for loc_item in item["loc"]):
                assert "empty" in item["msg"].lower() or "required" in item["msg"].lower(), "Slug validation msg should reference empty or required"
                found_slug = True
            if any("display_name" == loc_item for loc_item in item["loc"]):
                assert "empty" in item["msg"].lower() or "required" in item["msg"].lower(), "Display name msg should reference empty or required"
                found_display_name = True
        assert found_slug, "Validation error for empty slug not found in response."
        assert found_display_name, "Validation error for empty display_name not found in response."

    # Teardown: No persistent data created, no cleanup needed
