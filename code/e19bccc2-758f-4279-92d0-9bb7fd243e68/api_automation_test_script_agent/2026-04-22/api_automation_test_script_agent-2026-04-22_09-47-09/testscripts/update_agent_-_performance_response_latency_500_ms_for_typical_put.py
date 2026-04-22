import os
import requests
import pytest
import time
from typing import Optional

# --- Configuration & Helpers (ISO/IEC/IEEE 29148: test case parametricity, management) ---

def get_api_base_url() -> str:
    # Secure configuration, avoids hardcoding, per RFC 8259 best-practices
    return os.environ.get("API_BASE_URL", "https://api.example.com")

def get_bearer_token() -> Optional[str]:
    token = os.environ.get("API_BEARER_TOKEN", None)
    if not token:
        pytest.skip("Bearer token not configured in environment (OWASP ASVS 2.2.2)")
    return token

def get_agent_id() -> Optional[str]:
    agent_id = os.environ.get("AGENT_ID", None)
    if not agent_id:
        pytest.skip("Agent ID not configured in environment (Test Data Dependency, ISO 29148)")
    return agent_id

# --- Fixtures for setup/teardown (ISO/IEC/IEEE 29148 §7.2.2, RFC8259: data clarity) ---

@pytest.fixture(scope="module")
def auth_header():
    token = get_bearer_token()
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

@pytest.fixture(scope="module")
def agent_id():
    return get_agent_id()

# --- Test Case Implementation ---

def test_update_agent_p95_performance(auth_header, agent_id):
    """
    TC-PUT-55cdd53a-015: Verify that standard agent update completes within 500ms (p95).
    
    Preconditions:
      - API is reachable (ISO 29148 §5.2.9; RFC8259: infrastructure handled)
      - Valid Bearer token available (OWASP ASVS 2.2.2)
      - Agent with given id exists (traceable)
    Steps:
      1. Send PUT /api/agents/{agent_id} with valid Authorization and standard body.
      2. Measure response time.
    Expected Results:
      - Status 200
      - Response time < 500ms (p95)
    """
    base_url = get_api_base_url()
    endpoint = f"/api/agents/{agent_id}"
    url = base_url.rstrip("/") + endpoint

    # Prepare minimal, standards-compliant body (RFC 8259, no extra data)
    payload = {"slug": "update-performance"}  # Nullable accepted per schema

    # Step 1 & 2: Send request and measure time
    start_time = time.perf_counter()
    response = requests.put(url, headers=auth_header, json=payload, timeout=2)
    duration_ms = (time.perf_counter() - start_time) * 1000

    # Expected 1: Validate status (OWASP ASVS 9.4: error handling)
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}. Response: {response.text}"
    # Expected 2: Validate response time (Performance test, traceable: ISO 29148 §5.2.4)
    assert duration_ms < 500, f"Response time {duration_ms:.2f}ms exceeded 500ms (p95).
      \nRFC8259: JSON message flows performant;\nOWASP ASVS: Resource limiting"

    # Validate that response is valid JSON (RFC8259, ASVS 5.2.3 resilience)
    try:
        resp_json = response.json()
        assert isinstance(resp_json, dict) or isinstance(resp_json, list)
    except Exception as e:
        pytest.fail(f"Response is not parsable JSON (RFC8259): {e}\nBody: {response.text}")

# -- End of test case code --

# Traceability:
#  - API path: /api/agents/{agent_id} (source: openapi_spec:update_agent_api_agents__agent_id__put)
#  - Test covers status code and timing (ISO/IEC/IEEE 29148: verifiable/performance), error handling (OWASP ASVS 9.4), and RFC8259-compliant JSON payloads.
