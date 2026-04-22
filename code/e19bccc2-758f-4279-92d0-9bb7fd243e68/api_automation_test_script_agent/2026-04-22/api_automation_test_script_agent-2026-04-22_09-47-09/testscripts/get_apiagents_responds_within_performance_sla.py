import pytest
import requests
import time
from statistics import median, quantiles

# Compliance reference links
RFC_8259_URL = "https://tools.ietf.org/html/rfc8259"
OWASP_ASVS_URL = "https://owasp.org/www-project-application-security-verification-standard/"
ISO_IEEE_29148_URL = "https://www.iso.org/standard/72033.html"

@pytest.fixture(scope="session")
def api_base_url():
    # Base URL can be pulled from environment/config in a real implementation
    return "https://api.example.com"

@pytest.fixture(scope="session")
def bearer_token():
    # Token must be managed via secure vault/environment variable; placeholder for compliance
    token = pytest.config.getoption("--api-bearer-token")
    assert token, "Bearer token must be provided (OWASP ASVS V10: Secure Transmission)"
    return token

@pytest.fixture(scope="function")
def headers(bearer_token):
    return {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }

@pytest.fixture(scope="function")
def verify_api_reachability(api_base_url, headers):
    resp = requests.options(f"{api_base_url}/api/agents/", headers=headers)
    assert resp.status_code in [200, 204], (
        f"API reachability check failed (RFC8259 compliance): got {resp.status_code}"
    )

@pytest.mark.smoke
@pytest.mark.performance
def test_get_agents_performance_p95(api_base_url, headers, verify_api_reachability):
    """TC-GET-2e798b8e-09: Validate GET /api/agents/ P95 latency (<=500ms, OWASP ASVS V10)"""
    latencies = []
    status_codes = []
    for _ in range(100):
        start = time.time()
        resp = requests.get(f"{api_base_url}/api/agents/", headers=headers)
        elapsed = (time.time() - start) * 1000  # ms
        latencies.append(elapsed)
        status_codes.append(resp.status_code)

        # RFC8259: Verify JSON response formatting
        if resp.status_code == 200:
            try:
                resp.json()
            except ValueError:
                pytest.fail("Response is not valid JSON (RFC8259)")

    # ISO/IEC/IEEE 29148: Requirements Traceability
    # Validate all responses are HTTP 200
    assert all(code == 200 for code in status_codes), (
        "All GET /api/agents/ responses must be HTTP 200 as per requirement (ISO/IEC/IEEE 29148 Traceability)"
    )
    # Calculate P95
    p95 = quantiles(latencies, n=100)[94]
    assert p95 <= 500, (
        f"P95 latency must be <= 500 ms (OWASP ASVS V10): measured P95={p95:.2f} ms"
    )

    # Output compliance references for traceability
    print(f"Test aligned with:\nRFC 8259 (JSON response format): {RFC_8259_URL}\nOWASP ASVS V10 (Performance, Secure transmission): {OWASP_ASVS_URL}\nISO/IEC/IEEE 29148 (Requirements verification): {ISO_IEEE_29148_URL}")
