import pytest
import requests

API_BASE_URL = "<REPLACE_WITH_API_BASE_URL>"  # e.g., 'https://api.example.com'
BEARER_TOKEN = "<REPLACE_WITH_TOKEN>"  # Should be set via environment variable or secure vault

@pytest.fixture(scope="module")
def api_headers():
    return {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }

@pytest.fixture(scope="module")
def api_url():
    return f"{API_BASE_URL}/api/agents/"

@pytest.mark.regression
@pytest.mark.sanity
@pytest.mark.negative
def test_post_agents_missing_display_name(api_url, api_headers):
    """
    TC-POST-6e8d2c6f-003: Validate that omitting the required 'display_name' field returns 422 with validation error.
    Preconditions:
      - API is reachable
      - Valid bearer token available
    Steps:
      - Send POST request to /api/agents/ with slug and category only, omitting display_name.
    Expected Results:
      - Status 422
      - Response body contains 'detail' with validation error for missing display_name
    """
    # Arrange: Prepare payload omitting 'display_name'
    payload = {
        "slug": "agent-003",
        "category": "deployment"
    }

    # Act: Send POST request
    response = requests.post(api_url, headers=api_headers, json=payload)

    # Assert: Status code is 422
    assert response.status_code == 422, f"Expected status 422, got {response.status_code}. Response: {response.text}"

    # Assert: Response body contains 'detail' with validation error for missing display_name
    resp_json = response.json()
    assert "detail" in resp_json, "Response JSON does not contain 'detail' key."
    assert isinstance(resp_json["detail"], list), "'detail' should be a list of validation errors."

    # Find error for 'display_name' field
    display_name_error = None
    for err in resp_json["detail"]:
        if (
            isinstance(err, dict) and
            "loc" in err and
            isinstance(err["loc"], list) and
            "display_name" in err["loc"]
        ):
            display_name_error = err
            break
    assert display_name_error is not None, "No validation error found for missing 'display_name'."
    assert "msg" in display_name_error, "Validation error for 'display_name' missing 'msg' key."
    assert "type" in display_name_error, "Validation error for 'display_name' missing 'type' key."

    # Optionally, check error message content (implementation-specific)
    # assert display_name_error["msg"].lower().find("required") != -1
