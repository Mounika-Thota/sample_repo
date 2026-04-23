import pytest
import requests

BASE_URL = "http://localhost"  # Update as needed for the target API environment
\****************(scope="module")
def api_base_url():
    """Fixture for base API URL. Ensures centralized configuration."""
    return BASE_URL
\**********************\**********************\******************\******************("V2")
class TestGetAgentsAuthorization:
    """
    TestCase ID: TC-GET-2f1c1c7e-004
    Description: Validate that GET /api/agents/ returns an authentication error when an invalid Bearer token is provided.
    Standards: RFC 8259 (JSON), OWASP ASVS (V2), ISO/IEC/IEEE 29148 (requirements traceability)
    """

    endpoint = "/api/agents/"
    invalid_token = "invalid_token"

    def test_get_agents_with_invalid_token(self, api_base_url):
        """
        Step:
            Send GET request to /api/agents/ with Authorization header set to 'Bearer invalid_token'
        Expected Results:
            - Status 401 or 403
            - Error message indicating invalid authentication
        """
        url = f"{api_base_url}{self.endpoint}"
        headers = {
            "Authorization": f"Bearer {self.invalid_token}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        # Traceability: ISO/IEC/IEEE 29148 requirement verification for auth error

        # Assert: Status code is 401 or 403 (OWASP ASVS V2 - auth errors must not be ambiguous)
        assert response.status_code in [401, 403], (
            f"Expected status 401 or 403, got {response.status_code}. Response: {response.text}"
        )

        # Assert: Response is valid RFC 8259 JSON, or error message in allowed format
        try:
            error_body = response.json()
            # ISO/IEC/IEEE 29148: Verify presence of clear error messaging
            assert any(keyword in str(error_body).lower() for keyword in ["invalid", "unauthorized", "auth", "token"]), (
                f"Expected error message indicating invalid authentication, got: {error_body}"
            )
        except ValueError:
            # Non-JSON, ensure error message still present
            assert any(keyword in response.text.lower() for keyword in ["invalid", "unauthorized", "auth", "token"]), (
                f"Expected error message indicating invalid authentication, got: {response.text}"
            )

        # Traceability: This test fulfills OWASP ASVS V2 by negative testing for broken auth
        # Ensures all requirements are verifiable and verifiably failed when auth is inadequate
