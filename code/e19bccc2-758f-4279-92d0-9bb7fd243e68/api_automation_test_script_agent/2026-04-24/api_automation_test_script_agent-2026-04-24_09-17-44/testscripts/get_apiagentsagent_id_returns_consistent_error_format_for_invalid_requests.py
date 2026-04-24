import pytest
import requests
from typing import Dict, Any

BASE_URL = "https://api.example.com"  # Replace with actual base API URL
ENDPOINT_TEMPLATE = "/api/agents/{}"
\****************(scope="session")
def bearer_token() -> str:
    # In production, securely fetch/generate a valid token here
    token = "<REPLACE_WITH_TOKEN>"  # Placeholder as required by test case
    assert token and token != "<REPLACE_WITH_TOKEN>", "Bearer token must be set"
    return token

def validate_error_schema(response_json: Dict[str, Any]):
    # Enforce error schema as per OpenAPI spec, RFC8259 (valid JSON), OWASP ASVS, ISO/IEC/IEEE 29148 traceability
    assert 'detail' in response_json, "'detail' field must be present (OWASP ASVS, RFC8259)"
    assert isinstance(response_json['detail'], list), "'detail' must be a list (ISO/IEC/IEEE 29148)"
    for item in response_json['detail']:
        assert isinstance(item, dict), "Each 'detail' entry must be an object (RFC8259)"
        assert 'loc' in item, "Each error detail must have a 'loc' field (ISO/IEC/IEEE 29148)"
        assert 'msg' in item, "Each error detail must have a 'msg' field (ISO/IEC/IEEE 29148)"
        assert 'type' in item, "Each error detail must have a 'type' field (ISO/IEC/IEEE 29148)"
        assert all(isinstance(loc_value, (str, int)) for loc_value in item['loc']), "'loc' entries should be str or int (OpenAPI spec)"
        assert isinstance(item['msg'], str), "'msg' should be a string (OpenAPI spec)"
        assert isinstance(item['type'], str), "'type' should be a string (OpenAPI spec)"
\*************************("agent_id, scenario", [
    ("", "missing_id"),
    ("!@#$%", "invalid_id")
])
def test_get_agents_error_schema(agent_id, scenario, bearer_token):
    """
    TC-GET-2e2e0c6c-009: Validate /api/agents/{agent_id} error responses conform to error schema
    Compliance: RFC8259, OWASP ASVS, ISO/IEC/IEEE 29148
    """
    headers = {"Authorization": f"Bearer {bearer_token}"}
    if scenario == "missing_id":
        url = BASE_URL + "/api/agents/"  # missing path param
    else:
        url = BASE_URL + ENDPOINT_TEMPLATE.format(agent_id)
    response = requests.get(url, headers=headers)

    # Assert status code
    assert response.status_code == 422, f"Expected status 422, got {response.status_code} (OWASP ASVS, RFC8259)"

    # Assert valid RFC 8259 JSON
    try:
        json_body = response.json()
    except Exception as e:
        pytest.fail(f"Response is not valid JSON under RFC 8259: {str(e)}")
    
    # Validate error schema strictly
    validate_error_schema(json_body)
