import os
import uuid
import requests
import pytest

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
BEARER_TOKEN = os.getenv("API_BEARER_TOKEN")

# Example valid category from allowed list
VALID_CATEGORY = "testing"

# Expected response schema (to be filled as per API contract)
EXPECTED_RESPONSE_KEYS = {"id", "slug", "display_name", "category"}

@pytest.fixture(scope="module")
def auth_headers():
    assert BEARER_TOKEN, "Bearer token must be provided as API_BEARER_TOKEN environment variable."
    return {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }

def generate_unique_slug():
    return f"agent-{uuid.uuid4().hex[:8]}"

@pytest.fixture
def agent_payload():
    return {
        "slug": generate_unique_slug(),
        "display_name": "Agent One",  # Could be randomized if needed
        "category": VALID_CATEGORY
    }

# Cleanup logic if API supports deletion (pseudo-code)
def delete_agent_by_slug(slug, headers):
    # If the API supports DELETE, implement cleanup here
    # requests.delete(f"{BASE_URL}/api/agents/{slug}", headers=headers)
    pass

@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.functional
def test_create_agent_success(auth_headers, agent_payload):
    """
    Validate that creating an agent with valid slug, display_name, and category returns 200 and correct schema.
    """
    # Preconditions
    # 1. API is reachable
    health_resp = requests.get(f"{BASE_URL}/health")
    assert health_resp.status_code == 200, f"API health check failed: {health_resp.status_code}"

    # 2. Valid bearer token is provided (checked in fixture)

    # Step: Send POST request
    response = requests.post(
        f"{BASE_URL}/api/agents/",
        json=agent_payload,
        headers=auth_headers
    )

    # Expected Result 1: Status 200
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    # Expected Result 2: Response body matches expected schema
    resp_json = response.json()
    missing_keys = EXPECTED_RESPONSE_KEYS - resp_json.keys()
    assert not missing_keys, f"Missing keys in response: {missing_keys}"
    assert resp_json["slug"] == agent_payload["slug"], "Slug mismatch"
    assert resp_json["display_name"] == agent_payload["display_name"], "Display name mismatch"
    assert resp_json["category"] == agent_payload["category"], "Category mismatch"

    # Teardown: Optionally cleanup created agent
    try:
        delete_agent_by_slug(agent_payload["slug"], auth_headers)
    except Exception:
        pass
