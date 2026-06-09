import os
import json
import re
from typing import Any, Dict, Optional

import pytest
import requests

# Standards & compliance alignment (traceability notes)
# - RFC 8259: Validate response is valid JSON for controlled error bodies.
# - ISO/IEC/IEEE 29148: Verifiable requirements mapped to assertions (see R1-R5 below).
# - OWASP ASVS (V10 Error Handling & Logging): Ensure no sensitive internal errors/stack traces leak.

# Traceable, verifiable requirements (ISO/IEC/IEEE 29148 style)
# R1: When a server-side failure occurs during POST /login, the API SHALL return an HTTP 5xx status (expected: 500).
# R2: The response body SHALL be a valid JSON document (RFC 8259).
# R3: The JSON response SHALL contain a generic error 'code' (string) and 'message' (string).
# R4: The JSON response MAY contain 'traceId' as a string; if present it SHALL be a string.
# R5: The response body SHALL NOT expose stack traces or internal exception details (OWASP ASVS V10).


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            f"Set it to execute this test in your environment."
        )
    return value


def _build_url(base_url: str, endpoint: str) -> str:
    return base_url.rstrip("/") + "/" + endpoint.lstrip("/")


def _parse_json_response(resp: requests.Response) -> Dict[str, Any]:
    # R2: RFC 8259 JSON
    try:
        return resp.json()
    except ValueError as exc:
        body_preview = (resp.text or "")[:500]
        raise AssertionError(f"Response body is not valid JSON (RFC 8259). Body preview: {body_preview}") from exc


def _assert_schema(payload: Dict[str, Any]) -> None:
    # R3: code and message required
    assert isinstance(payload, dict), "Response JSON must be an object"

    assert "code" in payload, "Response JSON missing required field 'code'"
    assert "message" in payload, "Response JSON missing required field 'message'"

    assert isinstance(payload["code"], str), "Field 'code' must be a string"
    assert isinstance(payload["message"], str), "Field 'message' must be a string"

    # R4: traceId optional
    if "traceId" in payload and payload["traceId"] is not None:
        assert isinstance(payload["traceId"], str), "Field 'traceId' must be a string when present"


_SUSPECT_PATTERNS = [
    # Common stack trace indicators / internal exception leakage
    r"(?i)traceback\s*\(most\s+recent\s+call\s+last\)",
    r"(?i)exception\b",
    r"(?i)stack\s*trace\b",
    r"(?i)at\s+([a-zA-Z_$][\w$]*\.)+[A-Za-z_$][\w$]*\(.*:\d+\)",  # Java-like
    r"(?i)line\s+\d+",  # Python-like
    r"(?i)org\.springframework\.",
    r"(?i)java\.lang\.",
    r"(?i)com\.[a-z0-9_.]+\.",
    r"(?i)NullPointerException",
    r"(?i)SQLSTATE\b",
]


def _assert_no_stacktrace_leak(resp: requests.Response, payload: Dict[str, Any]) -> None:
    # R5: OWASP ASVS V10 - no internal details
    body_text = resp.text or ""
    searchable = body_text

    # Also check within structured fields
    try:
        searchable += "\n" + json.dumps(payload, ensure_ascii=False)
    except Exception:
        # If serialization fails for any reason, still validate raw text
        pass

    for pat in _SUSPECT_PATTERNS:
        if re.search(pat, searchable):
            raise AssertionError(
                f"Potential stack trace/internal details leaked (pattern: {pat}). "
                f"Response preview: {(body_text[:800] if body_text else '')}"
            )


@pytest.fixture(scope="session")
def config() -> Dict[str, str]:
    # Avoid hardcoded values; all environment-specific settings must be supplied.
    return {
        "base_url": _required_env("API_BASE_URL"),
        # Fault injection controls are environment-specific.
        # Provide either:
        # - A header-based switch (FAULT_INJECTION_HEADER/FAULT_INJECTION_VALUE), or
        # - A pre-created fault scenario id (FAULT_SCENARIO_ID) supported by your environment, or
        # - An out-of-band mechanism (set APPLY_FAULT_OUT_OF_BAND=true) and ensure the environment is already faulted.
        "fi_header": os.getenv("FAULT_INJECTION_HEADER", ""),
        "fi_value": os.getenv("FAULT_INJECTION_VALUE", ""),
        "fi_scenario_id": os.getenv("FAULT_SCENARIO_ID", ""),
        "apply_fault_out_of_band": os.getenv("APPLY_FAULT_OUT_OF_BAND", "false").lower(),
        # Credentials are required inputs, but any values are acceptable per test design.
        "username": _required_env("LOGIN_USERNAME"),
        "password": _required_env("LOGIN_PASSWORD"),
        # Optional: request timeout
        "timeout_seconds": os.getenv("HTTP_TIMEOUT_SECONDS", "15"),
    }


@pytest.fixture(scope="session")
def session() -> requests.Session:
    s = requests.Session()
    yield s
    s.close()


def _apply_fault_injection_headers(cfg: Dict[str, str]) -> Dict[str, str]:
    headers: Dict[str, str] = {"Content-Type": "application/json"}

    # Prefer explicit scenario ID header if provided
    if cfg.get("fi_scenario_id"):
        # Common convention; adapt via environment if needed
        headers["X-Fault-Scenario"] = cfg["fi_scenario_id"]

    # Generic header/value toggle if supported
    if cfg.get("fi_header") and cfg.get("fi_value"):
        headers[cfg["fi_header"]] = cfg["fi_value"]

    return headers


def test_tc_post_4b8cc9_020_controlled_5xx_no_stacktrace(session: requests.Session, config: Dict[str, str]) -> None:
    # Preconditions validation (fail fast with actionable message)
    out_of_band = config.get("apply_fault_out_of_band") == "true"
    has_header_toggle = bool(config.get("fi_header") and config.get("fi_value"))
    has_scenario = bool(config.get("fi_scenario_id"))

    assert (
        out_of_band or has_header_toggle or has_scenario
    ), (
        "Fault injection not configured. Provide one of: "
        "(1) APPLY_FAULT_OUT_OF_BAND=true with environment already faulted, "
        "(2) FAULT_SCENARIO_ID, "
        "(3) FAULT_INJECTION_HEADER and FAULT_INJECTION_VALUE."
    )

    url = _build_url(config["base_url"], "/login")

    # Step 1: Trigger server-side failure (done via configured fault injection mechanism)
    headers = _apply_fault_injection_headers(config)

    # Step 2: Send POST /login with any credentials (provided via env to avoid hardcoding)
    payload = {"username": config["username"], "password": config["password"]}

    timeout = float(config.get("timeout_seconds") or 15)
    resp = session.post(url, headers=headers, json=payload, timeout=timeout)

    # Expected results
    # R1: 5xx (expected 500 per test metadata)
    assert resp.status_code == 500, f"Expected HTTP 500, got {resp.status_code}. Body: {(resp.text or '')[:800]}"

    # R2-R4: Controlled JSON error schema
    data = _parse_json_response(resp)
    _assert_schema(data)

    # R5: No stack trace/internal exception leakage
    _assert_no_stacktrace_leak(resp, data)
