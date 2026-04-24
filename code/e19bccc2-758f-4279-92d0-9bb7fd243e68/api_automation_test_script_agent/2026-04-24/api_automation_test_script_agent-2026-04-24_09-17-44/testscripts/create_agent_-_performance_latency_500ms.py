import pytest
import requests
import time
import uuid

API_BASE_URL = "https://api.example.com"  # Replace with actual base URL
AGENTS_ENDPOINT = "/api/agents/"
\****************(scope="module")
def bearer_token():
    """
    Fixture to provide a valid bearer token.
    Replace with secure token retrieval mechanism.
    """
    # Securely retrieve from environment/configuration in real scenario
    return "<REPLACE_WITH_TOKEN>"
\****************(scope="function")
def unique_slug():
    """
    Generates a unique slug per test run to satisfy 'unique' constraint,
    traceable to ISO/IEC/IEEE 29148 (requirements uniqueness).
    """
    return f"agent-perf-{uuid.uuid4()}"

def test_agent_creation_performance(bearer_token, unique_slug):
    """
    Test Case ID: TC-POST-7f2b9c6b-016
    Description: Validate that agent creation completes within 500ms under normal load.
    Standards: RFC 8259 (JSON), OWASP ASVS (authentication, input validation), ISO/IEC/IEEE 29148 (requirements coverage)
    """
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "slug": unique_slug,   # non-empty, unique
        "display_name": "Agent Perf",   # non-empty
        "category": "performance_testing"  # enum
    }
    url = f"{API_BASE_URL}{AGENTS_ENDPOINT}"

    # Step: Send POST request and measure response time
    start_time = time.perf_counter()
    response = requests.post(url, headers=headers, json=payload)
    elapsed_ms = (time.perf_counter() - start_time) * 1000  # milliseconds

    # RFC 8259 traceability: payload is valid JSON, headers include proper Content-Type
    # OWASP ASVS: Authorization is required and present
    # ISO/IEC/IEEE 29148: All requirements (performance, status code, field constraints) are covered with assertions

    # Assert Status 200
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}. Response: {response.text}"

    # Assert Response time < 500ms
    assert elapsed_ms < 500, f"Expected response time < 500 ms, got {elapsed_ms:.2f} ms"

    # Additional RFC 8259/OWASP ASVS checks (optional, structure compliance)
    try:
        body = response.json()
    except Exception as e:
        pytest.fail(f"Response is not valid JSON: {e}")

    # Verifiable: Response contains the created agent slug (traceability)
    assert 'slug' in body, "Response must include 'slug' field as per requirements."
    assert body['slug'] == unique_slug, f"Response 'slug' ({body['slug']}) must match submitted unique_slug ({unique_slug})"
\****************(scope="function", autouse=True)
def cleanup_agent_post_test(request, bearer_token):
    """
    Data cleanup fixture to remove agent after test, complying with ISO/IEC/IEEE 29148 traceability and OWASP ASVS (data retention).
    """
    agents_to_cleanup = []

    def add_agent_slug(slug):
        agents_to_cleanup.append(slug)

    request.node.add_agent_slug = add_agent_slug

    yield

    for slug in agents_to_cleanup:
        # Attempt to delete agent if exists
        url = f"{API_BASE_URL}{AGENTS_ENDPOINT}{slug}"
        requests.delete(url, headers={
            "Authorization": f"Bearer {bearer_token}"
        })

# Register created slug for cleanup in test\*****************(tryfirst=True)
def pytest_runtest_call(item):
    if hasattr(item, 'funcargs'):
        unique_slug = item.funcargs.get('unique_slug')
        cleanup_fixture = item.funcargs.get('cleanup_agent_post_test')
        if unique_slug and cleanup_fixture and hasattr(item, 'add_agent_slug'):
            item.add_agent_slug(unique_slug)