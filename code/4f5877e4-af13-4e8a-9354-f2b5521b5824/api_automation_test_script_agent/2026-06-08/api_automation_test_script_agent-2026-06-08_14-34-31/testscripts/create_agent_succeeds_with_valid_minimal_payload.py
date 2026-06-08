import os
import json
import uuid
import pytest
import requests


# TC-POST-88971010-001
# Validate that POST /api/agents/ creates an agent when required fields are provided and request is authenticated.
# Standards alignment (traceable/verifiable):
# - ISO/IEC/IEEE 29148: verifiable requirement via explicit assertions for each expected result.
# - OWASP ASVS V2/V5 (and metadata V10): authenticated request, secure headers, and strict response validation.
# - RFC 8259: response body must be valid JSON.


def _get_env(name: str) -> str:
    value = os.getenv(name)
    if not value or not value.strip():
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value.strip()


@pytest.fixture(scope="session")
def base_url() -> str:
    # Do not hardcode environment-specific host; require configuration.
    return _get_env("API_BASE_URL").rstrip("/")


@pytest.fixture(scope="session")
def bearer_token() -> str:
    # Preconditions: Valid Bearer token available with permission to create agents.
    return _get_env("API_BEARER_TOKEN")


@pytest.fixture(scope="session")
def http_session() -> requests.Session:
    s = requests.Session()
    yield s
    s.close()


@pytest.fixture
def created_agent_slug():
    # Unique per test run to reduce collision risk without using dummy fixed values.
    # Still conforms to required 'string' constraint.
    return f"agent_min_{uuid.uuid4().hex[:12]}"


def _assert_json_rfc8259(response: requests.Response):
    # RFC 8259: ensure response body is valid JSON.
    try:
        return response.json()
    except ValueError as exc:
        body_preview = response.text[:500]
        raise AssertionError(f"Response body is not valid JSON (RFC 8259). Body preview: {body_preview}") from exc


def _assert_content_type_json(response: requests.Response):
    # Expected: application/json
    ct = response.headers.get("Content-Type", "")
    assert ct, "Missing Content-Type header in response"
    assert "application/json" in ct.lower(), f"Expected application/json Content-Type, got: {ct}"


@pytest.fixture
def cleanup_agent(base_url, bearer_token, http_session, request):
    # Teardown hook for cleanup when DELETE endpoint is available.
    # If not available, cleanup is skipped (best-effort) without failing the primary requirement verification.
    state = {"slug": None}

    def fin():
        slug = state.get("slug")
        if not slug:
            return
        delete_url = f"{base_url}/api/agents/{slug}"
        headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Accept": "application/json",
        }
        try:
            resp = http_session.delete(delete_url, headers=headers, timeout=30)
            # Do not assert status code for cleanup; API may not support delete.
            _ = resp
        except Exception:
            # Best-effort cleanup; ignore.
            pass

    request.addfinalizer(fin)
    return state


def test_tc_post_88971010_001_create_agent_authenticated_required_fields(
    base_url,
    bearer_token,
    http_session,
    created_agent_slug,
    cleanup_agent,
):
    # Preconditions:
    # - API is reachable (validated implicitly by receiving a response; network errors will fail test)
    # - Valid Bearer token available with permission to create agents (validated by expected 200)

    url = f"{base_url}/api/agents/"
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Body parameters (required): slug (string), display_name (string), category (enum)
    payload = {
        "slug": created_agent_slug,
        "display_name": f"Agent Minimal {created_agent_slug}",
        "category": "testing",
    }

    # Step: Send POST request to /api/agents/ with Authorization header and valid JSON body
    response = http_session.post(url, headers=headers, json=payload, timeout=30)

    # Expected result: Status 200
    assert response.status_code == 200, (
        f"Expected status 200, got {response.status_code}. "
        f"Response body preview: {response.text[:500]}"
    )

    # Expected result: Response Content-Type is application/json
    _assert_content_type_json(response)

    # Expected result: Response body is valid JSON (RFC 8259)
    response_json = _assert_json_rfc8259(response)

    # Persist for best-effort cleanup
    cleanup_agent["slug"] = created_agent_slug

    # Additional verifiable checks consistent with requirement intent (non-breaking, schema-agnostic):
    # Ensure response JSON is an object/dict (typical for create endpoints)
    assert isinstance(response_json, (dict, list)), "Expected JSON response to be an object or array"

    # If response is an object, verify it at least echoes/contains created identifiers when present.
    if isinstance(response_json, dict):
        if "slug" in response_json:
            assert response_json["slug"] == created_agent_slug, "Response 'slug' does not match request"
        if "display_name" in response_json:
            assert response_json["display_name"] == payload["display_name"], "Response 'display_name' does not match request"
        if "category" in response_json:
            assert response_json["category"] == payload["category"], "Response 'category' does not match request"
