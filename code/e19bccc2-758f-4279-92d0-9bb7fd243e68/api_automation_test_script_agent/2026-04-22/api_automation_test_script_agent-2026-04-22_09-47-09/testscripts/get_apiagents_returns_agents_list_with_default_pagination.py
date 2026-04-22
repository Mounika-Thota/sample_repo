import os
import pytest
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
BEARER_TOKEN = os.getenv("API_BEARER_TOKEN", None)

@pytest.fixture(scope="session")
def auth_header():
    """Provide Authorization header if token is configured."""
    if not BEARER_TOKEN:
        pytest.skip("Bearer token is not configured in environment variable API_BEARER_TOKEN.")
    return {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }

def is_json_content_type(headers):
    content_type = headers.get("Content-Type", "")
    # Align with RFC 8259 - Accept 'application/json' and possible UTF-8 parameters
    return content_type.startswith("application/json")

def is_array_json(response_json):
    return isinstance(response_json, list)

@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.ASVS("V2")
@pytest.mark.ASVS("V10")
def test_get_agents_list_default_params(auth_header):
    """
    Traceability:
      - RFC 8259 (JSON content and Content-Type)
      - OWASP ASVS V2: Authentication, access control on API endpoints
      - OWASP ASVS V10: Validation for safe API responses
      - ISO/IEC/IEEE 29148: Requirements are traceable and verifiable from test case
    """
    endpoint = f"{API_BASE_URL}/api/agents/"
    params = {"skip": 0, "limit": 100}
    
    with pytest.assume:
        # Step 1: Send GET request
        response = requests.get(endpoint, headers=auth_header, params=params, timeout=15)

        # Expected Result 1: Status 200
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        # Expected Result 2: Response body is JSON array/list of agents
        try:
            response_json = response.json()
        except Exception as ex:
            pytest.fail(f"Response is not valid JSON as per RFC 8259: {str(ex)}")
        assert is_array_json(response_json), (
            "Response is not a JSON array (RFC 8259 compliance) as required by API contract."
        )

        # Expected Result 3: Content-Type is 'application/json' (RFC 8259)
        assert is_json_content_type(response.headers), (
            f"Content-Type is not application/json: {response.headers.get('Content-Type','')}"
        )
