import pytest
import requests

# Constants and expected values
BASE_URL = "https://api.yourdomain.com"  # Replace with actual base URL per env config
AGENT_ID = "<REPLACE_WITH_AGENT_ID>"  # Parameterized: Should be injected via fixtures or CI variables
BEARER_TOKEN = "<REPLACE_WITH_TOKEN>"   # Parameterized: Should be injected securely
ENDPOINT = f"/api/agents/{AGENT_ID}"

# Allowed values (for traceability against requirements)
ALLOWED_CATEGORY_ENUM = [
    "usg", "testing", "api_doc_testing", "performance_testing",
    "deployment", "req_synthesizer", "ui_automation", "documentation", None
]

@pytest.fixture(scope="module")
def api_headers():
    """
    Precondition: Valid Bearer token available.
    Follows RFC 8259 for Content-Type; ensures compliance with ISO/IEC/IEEE 29148 for header parameterization.
    """
    return {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }

@pytest.fixture(scope="module")
def agent_exists():
    """
    Precondition: Agent with AGENT_ID exists.
    OWASP ASVS: Ensures input is not arbitrary, maintaining secure state.
    """
    # Typically, check or create the agent. For test integrity, assert existence here (example only).
    url = BASE_URL + ENDPOINT
    response = requests.get(url, headers={"Authorization": f"Bearer {BEARER_TOKEN}"})
    assert response.status_code == 200, f"Precondition failed: Agent {AGENT_ID} should exist"
    return True

@pytest.mark.regression
@pytest.mark.sanity
def test_put_agent_category_invalid_enum(api_headers, agent_exists):
    """
    TC-PUT-55cdd53a-008
    Validate update fails with 422 if 'category' field is not one of allowed enum values or null.
    Requirements tracing:
        - RFC 8259: All payloads use compliant JSON and Content-Type headers.
        - OWASP ASVS (V5, V10): Only allowed (whitelisted) enums are accepted.
        - ISO/IEC/IEEE 29148: Trace back to OpenAPI spec definition (parameter constraints).
    """
    invalid_category = "invalid_category"
    assert invalid_category not in ALLOWED_CATEGORY_ENUM, "Test setup error: category value should be invalid per specification."
    payload = {"category": invalid_category}

    url = BASE_URL + ENDPOINT

    response = requests.put(url, headers=api_headers, json=payload)

    # Assert: Status 422 (Unprocessable Entity)
    assert response.status_code == 422, (
        f"Expected status 422 for invalid category, got {response.status_code}: {response.text}"
    )

    # Assert: Response must conform to expected validation error schema
    # Per OpenAPI spec: {'detail': [{'loc': ['string', 'integer'], 'msg': 'string', 'type': 'string'}]}
    # Strict JSON conformance per RFC 8259
    resp_json = response.json()
    assert "detail" in resp_json,
        f"Validation error response must include 'detail' field. Got: {resp_json}"
    assert isinstance(resp_json["detail"], list), "'detail' must be a list (per schema)."
    for err in resp_json["detail"]:
        assert isinstance(err, dict), f"Each error in 'detail' must be an object. Got: {err}"
        assert all(k in err for k in ["loc", "msg", "type"]), (
            f"Each error must include 'loc', 'msg', and 'type'. Got: {err}"
        )
        assert isinstance(err["loc"], list), f"'loc' must be a list. Got: {err}"
        assert isinstance(err["msg"], str), "'msg' must be a string."
        assert isinstance(err["type"], str), "'type' must be a string."

    # ISO/IEC/IEEE 29148: Each expected requirement is verified and outcome asserted.

# No teardown needed (no side effects from this immutable negative test case)
