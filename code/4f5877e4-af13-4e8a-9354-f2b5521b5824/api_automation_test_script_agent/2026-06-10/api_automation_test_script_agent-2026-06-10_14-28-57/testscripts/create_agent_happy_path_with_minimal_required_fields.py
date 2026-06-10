import os
import uuid
import re
import json
import pytest
import requests

# Test Case: TC-POST-ccfbea19-001
# Standards/Compliance Traceability (inferred):
# - ISO/IEC/IEEE 29148: clear, verifiable requirements mapped to assertions below.
# - RFC 8259: response must be valid JSON.
# - OWASP ASVS (V2/V5/V10): authn/authz via Bearer token; avoid leaking sensitive data.


SENSITIVE_KEY_PATTERNS = [
    re.compile(r"password", re.IGNORECASE),
    re.compile(r"passphrase", re.IGNORECASE),
    re.compile(r"secret", re.IGNORECASE),
    re.compile(r"token", re.IGNORECASE),
    re.compile(r"api[_-]?key", re.IGNORECASE),
    re.compile(r"authorization", re.IGNORECASE),
    re.compile(r"private[_-]?key", re.IGNORECASE),
    re.compile(r"session", re.IGNORECASE),
    re.compile(r"cookie", re.IGNORECASE),
]

SENSITIVE_VALUE_PATTERNS = [
    re.compile(r"Bearer\s+[A-Za-z0-9\-\._~\+\/]+=*", re.IGNORECASE),
    re.compile(r"eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+"),  # JWT-like
]


def _base_url() -> str:
    base = os.getenv("API_BASE_URL", "").strip()
    if not base:
        raise RuntimeError("API_BASE_URL environment variable must be set (e.g., https://api.example.com)")
    return base.rstrip("/")


def _bearer_token() -> str:
    token = os.getenv("API_BEARER_TOKEN", "").strip()
    if not token:
        raise RuntimeError("API_BEARER_TOKEN environment variable must be set")
    return token


def _build_headers() -> dict:
    return {
        "Authorization": f"Bearer {_bearer_token()}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _unique_slug(prefix: str = "qa-agent-min") -> str:
    # Preconditions: slug must be unique for this run.
    # Use UUID suffix to avoid collisions without hardcoding.
    return f"{prefix}-{uuid.uuid4().hex[:10]}"


def _iter_json_paths(obj, path="$"):
    if isinstance(obj, dict):
        for k, v in obj.items():
            kp = f"{path}.{k}"
            yield kp, k, v
            yield from _iter_json_paths(v, kp)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            kp = f"{path}[{i}]"
            yield kp, None, v
            yield from _iter_json_paths(v, kp)


def _assert_no_sensitive_data_in_json(json_obj):
    # OWASP ASVS: prevent sensitive data exposure in responses.
    for jp, key, value in _iter_json_paths(json_obj):
        if key is not None:
            for pat in SENSITIVE_KEY_PATTERNS:
                assert not pat.search(str(key)), f"Sensitive key name found at {jp}: {key}"

        # Check string values for token-like artifacts
        if isinstance(value, str):
            for pat in SENSITIVE_VALUE_PATTERNS:
                assert not pat.search(value), f"Sensitive value pattern found at {jp}"


def _assert_content_type_json(resp: requests.Response):
    ct = resp.headers.get("Content-Type", "")
    assert "application/json" in ct.lower(), f"Expected application/json Content-Type, got: {ct}"


def _parse_json_rfc8259(resp: requests.Response):
    # RFC 8259: response must be valid JSON text.
    # Use json.loads on raw text to strictly validate JSON syntax.
    raw = resp.text
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        raise AssertionError(f"Response body is not valid JSON (RFC 8259). Error: {e}. Body: {raw[:500]}")
    return parsed


@pytest.fixture(scope="session")
def http_session():
    s = requests.Session()
    yield s
    s.close()


@pytest.fixture(scope="session")
def api_base_url():
    # Preconditions: API base URL is reachable.
    # Reachability will be implicitly validated by successful request/response.
    return _base_url()


@pytest.fixture(scope="session")
def auth_headers():
    # Preconditions: Valid Bearer token available with permission to create agents.
    return _build_headers()


@pytest.fixture()
def created_agent_slug():
    return _unique_slug("qa-agent-min")


def _cleanup_agent_if_supported(http_session: requests.Session, base_url: str, headers: dict, agent_id_or_slug: str):
    # Best-effort cleanup if API supports deletion. Not part of the described endpoint contract.
    # Attempt common patterns; ignore failures to avoid masking creation test result.
    candidate_paths = [
        f"/api/agents/{agent_id_or_slug}",
        f"/api/agents/{agent_id_or_slug}/",
    ]
    for path in candidate_paths:
        try:
            http_session.delete(f"{base_url}{path}", headers=headers, timeout=30)
        except Exception:
            pass


def test_post_agents_create_minimal_fields_returns_200_json_and_no_sensitive_data(
    http_session,
    api_base_url,
    auth_headers,
    created_agent_slug,
):
    # Steps:
    # 1) Send POST request to /api/agents/ with Authorization: Bearer <TOKEN> and JSON content
    # 2) Body contains required fields: slug, display_name, category

    url = f"{api_base_url}/api/agents/"
    payload = {
        "slug": created_agent_slug,
        "display_name": "QA Agent Minimal 001",
        "category": "testing",
    }

    resp = http_session.post(url, headers=auth_headers, json=payload, timeout=30)

    # Expected results / Verifiable requirements (ISO/IEC/IEEE 29148):
    # R1: Status 200
    assert resp.status_code == 200, f"Expected HTTP 200, got {resp.status_code}. Body: {resp.text[:500]}"

    # R2: Response Content-Type is application/json
    _assert_content_type_json(resp)

    # R3: Response body is valid JSON (RFC 8259)
    parsed = _parse_json_rfc8259(resp)

    # R4: No sensitive data returned in error or success payload
    _assert_no_sensitive_data_in_json(parsed)

    # Optional: basic sanity that response is JSON object or array (still RFC8259-compliant)
    assert isinstance(parsed, (dict, list)), f"Expected JSON object or array, got {type(parsed)}"

    # Teardown: best-effort cleanup to keep environment stable.
    # Prefer an explicit id if provided, else fallback to slug.
    agent_identifier = None
    if isinstance(parsed, dict):
        agent_identifier = parsed.get("id") or parsed.get("slug")

    if agent_identifier:
        _cleanup_agent_if_supported(http_session, api_base_url, auth_headers, str(agent_identifier))
    else:
        _cleanup_agent_if_supported(http_session, api_base_url, auth_headers, created_agent_slug)
