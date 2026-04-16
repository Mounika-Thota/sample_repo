import os
import re
from urllib.parse import urljoin

import pytest
import requests


# Test Case: TC-GET-7b6cf9d0-002
# Description: Validate that the health endpoint is publicly accessible because the operation declares no security requirements.
# Standards traceability:
# - ISO/IEC/IEEE 29148: Requirement completeness/consistency -> verifies implemented behavior matches declared empty security requirements.
# - OWASP ASVS V2 (Authentication): verifies endpoint access control aligns with specification (public endpoint).


def _get_base_url() -> str:
    base_url = os.getenv("API_BASE_URL")
    if not base_url:
        raise RuntimeError(
            "API_BASE_URL environment variable must be set (e.g., https://api.example.com)."
        )
    return base_url.rstrip("/") + "/"


def _is_auth_challenge_present(response: requests.Response) -> bool:
    """Returns True if response indicates an authentication challenge is required."""
    # Per RFC 7235, WWW-Authenticate is used in 401 responses to indicate auth challenge.
    www_auth = response.headers.get("WWW-Authenticate")
    if response.status_code == 401 and www_auth:
        return True

    # Some gateways misuse 403 with challenge headers; treat that as challenge too.
    if response.status_code in (401, 403) and www_auth:
        return True

    return False

\****************(scope="session")
def api_base_url() -> str:
    # Preconditions: API base URL is known and reachable
    return _get_base_url()

\****************(scope="session")
def http_session() -> requests.Session:
    session = requests.Session()
    yield session
    session.close()


def test_health_endpoint_public_access_no_auth_header(api_base_url: str, http_session: requests.Session):
    """Validate /health is accessible without Authorization header."""

    # Steps: Send a GET request to /health without Authorization header
    url = urljoin(api_base_url, "health")
    headers = {
        "Accept": "application/json",
        # Intentionally no Authorization header
    }

    response = http_session.get(url, headers=headers, timeout=30)

    # Expected results: Status 200
    assert response.status_code == 200, (
        f"Expected HTTP 200 from GET /health without Authorization, got {response.status_code}. "
        f"Response body: {response.text[:500]}"
    )

    # Expected results: No authentication challenge required for success
    # (no mandatory WWW-Authenticate to access)
    assert not _is_auth_challenge_present(response), (
        "Response indicates an authentication challenge (unexpected for a public endpoint). "
        f"Status: {response.status_code}, WWW-Authenticate: {response.headers.get('WWW-Authenticate')}"
    )

    # Additional verifiable check: ensure the server did not redirect to a login/auth flow.
    # This supports OWASP ASVS V2 intent (no auth required) without adding new functional requirements.
    assert response.url == url, (
        f"Unexpected redirect observed for public /health endpoint. Requested: {url}, Final: {response.url}"
    )
