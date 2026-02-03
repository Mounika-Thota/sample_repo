import pytest
import requests

API_BASE_URL = "http://localhost"  # Replace with actual base URL if needed
ENDPOINT = "/api/auth/token"

@pytest.fixture(scope="module")
def api_url():
    return f"{API_BASE_URL}{ENDPOINT}"

@pytest.fixture(scope="module")
def session():
    s = requests.Session()
    yield s
    s.close()

class TestPostAuthTokenMissingApiKey:
    def test_missing_x_api_key_header(self, api_url, session):
        """
        Validate that omitting the required x-api-key header results in a 422 Validation Error
        with the correct error schema.
        """
        # Preconditions: API is reachable
        try:
            health_resp = session.get(API_BASE_URL)
            assert health_resp.status_code < 500, "API is not reachable"
        except Exception as e:
            pytest.skip(f"API not reachable: {e}")

        # Step: Send POST request to /api/auth/token without the x-api-key header
        headers = {
            "Content-Type": "application/json"
            # x-api-key intentionally omitted
        }
        response = session.post(api_url, headers=headers)

        # Expected Result 1: Status 422
        assert response.status_code == 422, f"Expected status 422, got {response.status_code}"

        # Expected Result 2: Response body contains 'detail' field with validation error details
        json_body = response.json()
        assert "detail" in json_body, "Response body missing 'detail' field"
        assert isinstance(json_body["detail"], list), "'detail' field is not a list"
        # Validate error schema for each item in detail
        for item in json_body["detail"]:
            assert "loc" in item and isinstance(item["loc"], list), "Each error must have 'loc' as list"
            assert all(isinstance(loc_elem, (str, int)) for loc_elem in item["loc"]), "'loc' elements must be string or integer"
            assert "msg" in item and isinstance(item["msg"], str), "Each error must have 'msg' as string"
            assert "type" in item and isinstance(item["type"], str), "Each error must have 'type' as string"
