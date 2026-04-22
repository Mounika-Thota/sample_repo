import pytest
import requests

# ISO/IEC/IEEE 29148: Traceability - Link Test ID and Requirements
# OWASP ASVS: V5, V10 - Input Validation, Error Handling
# RFC 8259: JSON Response Compliance

BASE_URL = "https://api.example.com"  # Must be parametrized as needed
ENDPOINT = "/api/agents/{agent_id}"

@pytest.fixture(scope="session")
def bearer_token():
    # This should be replaced as per authentication mechanism
    # For compliance, bearer token acquisition should be traceable & secure (ISO/IEC/IEEE 29148)
    return "<REPLACE_WITH_TOKEN>"

@pytest.fixture(scope='session')
def api_url():
    return BASE_URL

@pytest.mark.regression
@pytest.mark.input_validation
@pytest.mark.owasp_v5
@pytest.mark.owasp_v10
@pytest.mark.traceability_tc("TC-DELETE-f2e6c865-002")
def test_delete_agent_malformed_agent_id(api_url, bearer_token):
    malformed_agent_id = "!nvalid_id"
    url = f"{api_url}{ENDPOINT.format(agent_id=malformed_agent_id)}"
    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json"
    }

    # Preconditions: API is reachable, Valid Bearer token
    response = requests.delete(url, headers=headers)

    # RFC 8259 compliance: Response must be valid JSON, status 422, and schema-compliant error details
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
    try:
        json_body = response.json()
    except ValueError as e:
        pytest.fail(f"Response body not RFC 8259 compliant JSON: {str(e)}")
    
    # Validation against expected schema
    assert 'detail' in json_body, "'detail' missing in response body per schema"
    assert isinstance(json_body['detail'], list), "'detail' should be an array per RFC 8259 and API schema"
    for error in json_body['detail']:
        assert 'loc' in error and isinstance(error['loc'], list), "Each error must have 'loc' (array per schema)"
        # ISO/IEC/IEEE 29148: Each error must be traceable to malformed input
        assert any(isinstance(i, str) or isinstance(i, int) for i in error['loc']), "'loc' should contain strings/integers"
        assert 'msg' in error and isinstance(error['msg'], str), "Each error must contain 'msg' (string per schema)"
        assert 'type' in error and isinstance(error['type'], str), "Each error must contain 'type' (string per schema)"

    # OWASP ASVS compliance: No internal error detail, only safe validation error info
    for error in json_body['detail']:
        assert not ('exception' in error['msg'].lower() or 'traceback' in error['msg'].lower()), "Error messages must not expose internals (OWASP ASVS V10)"

    
@pytest.hookimpl(tryfirst=True)
def pytest_metadata(metadata):
    metadata['OWASP ASVS'] = 'V5,V10'
    metadata['ISO/IEC/IEEE 29148'] = 'traceability,test design'
    metadata['RFC 8259'] = 'JSON compliance'
