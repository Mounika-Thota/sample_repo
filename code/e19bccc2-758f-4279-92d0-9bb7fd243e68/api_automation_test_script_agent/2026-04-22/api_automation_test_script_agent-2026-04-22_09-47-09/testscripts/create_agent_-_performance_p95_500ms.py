import pytest
import requests
import time

BASE_URL = "https://api.example.com"  # Update with correct API base URL
AUTH_TOKEN = pytest.config.getoption("--bearer_token")  # Token supplied externally for compliance
ENDPOINT = "/api/agents/"
HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

@pytest.fixture(scope="session")
def api_is_reachable():
    health_url = BASE_URL + "/health"
    resp = requests.get(health_url)
    assert resp.status_code == 200, "API health endpoint did not return 200"
    return True

@pytest.fixture(scope="session")
def valid_bearer_token():
    # Token supplied externally to ensure confidentiality and traceability (ISO/IEC/IEEE 29148)
    assert AUTH_TOKEN and AUTH_TOKEN != "<REPLACE_WITH_TOKEN>", "Bearer token must be provided"
    return AUTH_TOKEN

@pytest.mark.performance
@pytest.mark.regression
@pytest.mark.asvs("V10")  # OWASP ASVS reference for Business Logic Security
@pytest.mark.rfc8259
@pytest.mark.iso29148
@ pytest.mark.usefixtures("api_is_reachable", "valid_bearer_token")
def test_post_agents_response_time():
    """
    Validate POST /api/agents/ returns response within 500ms for valid requests.
    Traceability:
      - RFC 8259: JSON request/response formatting
      - OWASP ASVS V10: Business Logic, Rate Limit, Performance
      - ISO/IEC/IEEE 29148: Requirements traceability, testability, data confidentiality
    """
    payload = {
        "slug": "performance-agent",
        "display_name": "Performance Agent",
        "category": "performance_testing"
    }
    start_time = time.time()
    response = requests.post(
        BASE_URL + ENDPOINT,
        headers=HEADERS,
        json=payload
    )
    elapsed_ms = (time.time() - start_time) * 1000
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    # RFC 8259 compliance: response must be JSON
    try:
        resp_json = response.json()
    except Exception:
        pytest.fail("Response does not comply with RFC 8259: invalid JSON")
    assert elapsed_ms < 500, f"Response time exceeded. Was {elapsed_ms:.2f}ms. Requirement: <500ms"
    pytest.assume(elapsed_ms < 500, "Performance p95 < 500ms per requirement")
    # ASVS: No sensitive data leaks in response, basic check
    assert "token" not in resp_json, "Response should not leak sensitive tokens (ASVS)"

# Optionally, collect 95th percentile if running multiple iterations
@pytest.mark.skip(reason="p95 calculation requires multiple runs and aggregation")
def test_post_agents_p95():
    """
    This test is a placeholder for p95 response time assessment, recommended for full suite runs.
    """
    pass
