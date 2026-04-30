import pytest
import requests

# ISO/IEC/IEEE 29148: Test Case traceability and requirements verification
# RFC 8259: Ensuring JSON response compliance
# OWASP ASVS V2, V5, V10: Authentication, Input Validation, Response Structure

class TestGetAgent:
    API_URL = "https://your-api-domain.com"  # <-- Replace with actual base URL

    @pytest.fixture(scope="class", autouse=True)
    def setup_class(cls, request):
        """
        Setup fixture to retrieve valid bearer token and agent_id.
        Requirements trace:
         - Precondition: API is reachable, valid bearer token, valid agent_id.
        """
        # -- Implement: Retrieve or generate valid bearer token securely
        # -- Implement: Retrieve valid agent_id existing in the system
        # For ISO/IEC/IEEE 29148 traceability, parameters should be externally managed
        # The following assumes this info can be supplied from environment or a fixture
        cls.bearer_token = request.config.getoption("--bearer-token")
        cls.agent_id = request.config.getoption("--agent-id")
        if not all([cls.bearer_token, cls.agent_id]):
            pytest.skip("Bearer token and valid agent_id must be provided via pytest options.")
    
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.sanity
    def test_get_agent_details(self):
        """
        TC-GET-8b5c6fa9-001
        Validate that GET /api/agents/{agent_id} returns agent details for a valid and existing agent_id with HTTP 200.
        Standards: ISO/IEC/IEEE 29148 (requirements trace), RFC 8259 (JSON compliance), OWASP ASVS V2,V5,V10
        """
        endpoint = f"{self.API_URL}/api/agents/{self.agent_id}"
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }

        # Step: Send GET request
        response = requests.get(endpoint, headers=headers)

        # Expected Result #1: Status code is 200
        assert response.status_code == 200, f"Expected HTTP 200, got {response.status_code}. OWASP ASVS V2: Authentication check, V10: Error handling compliance."

        # Expected Result #2: Response is application/json (RFC 8259 compliance)
        content_type = response.headers.get("Content-Type", "")
        assert "application/json" in content_type, f"Expected Content-Type: application/json, got {content_type}. RFC 8259 compliant."

        # Expected Result #3: Response body matches expected agent schema (ISO/IEC/IEEE 29148 requirement verification)
        body = response.json()

        # -- Agent schema: Extract schema from openapi or requirements contract if available
        # For compliance, schema should be referenced externally; placeholder below
        expected_keys = {"id", "name", "email", "status"}  # <-- Replace with actual schema fields
        missing_keys = expected_keys.difference(body.keys())
        assert not missing_keys, f"Missing keys in agent response: {missing_keys}. ISO/IEC/IEEE 29148: Schema verification."

        # OWASP ASVS V5: Input/Output Validation
        assert isinstance(body["id"], str), "Agent 'id' should be a string as per schema."
        assert isinstance(body["name"], str), "Agent 'name' should be a string as per schema."
        assert isinstance(body["email"], str), "Agent 'email' should be a string as per schema."
        assert body["status"] in ["active", "inactive"], "Agent 'status' value must be valid."

    @pytest.fixture(scope="class", autouse=True)
    def teardown_class(cls):
        """
        Clean up if any teardown is required (ISO/IEC/IEEE 29148 compliance).
        """
        # No data modification in this test; placeholder for potential future teardown
        pass
