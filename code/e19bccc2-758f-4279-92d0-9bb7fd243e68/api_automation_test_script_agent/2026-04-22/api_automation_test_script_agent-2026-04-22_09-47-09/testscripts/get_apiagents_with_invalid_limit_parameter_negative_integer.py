import pytest
import requests

def pytest_addoption(parser):
    parser.addoption(
        "--base-url", action="store", default=None, help="Base API URL, e.g. https://api.example.com"
    )
    parser.addoption(
        "--token", action="store", default=None, help="Bearer token for authentication"
    )

@pytest.fixture(scope="session")
def base_url(request):
    url = request.config.getoption("--base-url")
    assert url, "Base URL (--base-url) must be provided per ISO/IEC/IEEE 29148 requirement."
    return url.rstrip("/")

@pytest.fixture(scope="session")
def bearer_token(request):
    token = request.config.getoption("--token")
    assert token and token != "<REPLACE_WITH_TOKEN>", "Valid Bearer token is required for RFC 8259 compliance."
    return token

@pytest.fixture(scope="function")
def api_headers(bearer_token):
    return {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }

@pytest.mark.owasp_asvs(["V5", "V10"])
@pytest.mark.regression
@pytest.mark.boundary
@pytest.mark.test_id("TC-GET-2e798b8e-03")
def test_negative_limit_schema_validation(base_url, api_headers):
    """
    Validate error response when limit query parameter is negative, violating schema.
    Requirements:
        - RFC 8259: Strict JSON error schema parsing
        - OWASP ASVS: V5, V10
        - ISO/IEC/IEEE 29148: Traceable, verifiable, and unambiguous negative test case
    """
    endpoint = f"{base_url}/api/agents/"
    params = {"limit": -5}

    response = requests.get(endpoint, headers=api_headers, params=params)

    # Assert status
    assert response.status_code == 422, (
        f"Expected status 422 per API contract. Got {response.status_code}. "
        f"Refer RFC 8259/OWASP ASVS for proper error status handling."
    )

    # Validate JSON response
    try:
        payload = response.json()
    except Exception as e:
        pytest.fail(f"Response body is not valid JSON (RFC 8259): {e}")

    # Expected schema
    assert "detail" in payload, "'detail' missing from error body as per HTTPValidationError schema."
    assert isinstance(payload["detail"], list), "'detail' value must be a list."
    found = False
    for detail_item in payload["detail"]:
        assert isinstance(detail_item, dict), "'detail' items must be objects per schema."
        if (
            detail_item.get("loc") == ["query", "limit"] and
            detail_item.get("type", "").startswith("type_error.integer")
        ):
            assert "must be a positive integer" in detail_item.get("msg", ""), (
                "Detail message should reference 'must be a positive integer' for negative validation error."
            )
            found = True
    assert found, (
        "HTTPValidationError for parameter 'limit' (negative value) not found in response. "
        "See ISO/IEC/IEEE 29148 traceability."
    )
