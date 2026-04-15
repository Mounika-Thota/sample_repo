import pytest
import requests
import json

# ISO/IEC/IEEE 29148 & RFC 8259 compliance: Clearly defined requirement and traceable expected outcomes.
# OWASP ASVS V5, V10: Ensuring proper response content negotiation and error handling.

API_BASE_URL = "http://localhost:8000"  # Replace with your real API base URL or use pytest configuration
\****************(scope="module")
def health_endpoint_url():
    """Provides the /health endpoint URL. ISO/IEC/IEEE 29148: Clear dependency injection for traceability."""
    return f"{API_BASE_URL}/health"


def is_valid_json(response_text):
    """RFC 8259: Validates if the provided text is a valid JSON document."""
    try:
        json.loads(response_text)
        return True
    except ValueError:
        return False


def test_health_get_with_uncommon_accept_header(health_endpoint_url):
    """TC-GET-07e6fdc4-002: Validate /health accepts uncommon Accept header and returns compliant JSON.
    Standards traceability:
    - ISO/IEC/IEEE 29148: Test steps and verifications are mapped to requirements.
    - RFC 8259: Response must be valid JSON.
    - OWASP ASVS V5 (Validation, Encoding and Injection Prevention), V10 (Error Handling and Logging): Checks are in place.
    """

    # Precondition: API endpoint /health is reachable
    # (Optionally verify availability before test)
    preq = requests.get(health_endpoint_url)
    assert preq.status_code < 500, "Precondition failed: /health endpoint is not reachable (5xx encountered)."

    # Step: Send GET /health with Accept: application/xml (uncommon/mismatched Accept)
    headers = {"Accept": "application/xml"}
    response = requests.get(health_endpoint_url, headers=headers)

    # Expected Result 1: Status 200
    assert response.status_code == 200, (
        f"Expected HTTP 200 OK, got {response.status_code}. Trace: TC-GET-07e6fdc4-002, ISO/IEC/IEEE 29148 req."
    )

    # Expected Result 2: Response Content-Type is application/json
    content_type = response.headers.get("Content-Type", "")
    assert content_type.startswith("application/json"), (
        f"Expected Content-Type 'application/json', got '{content_type}'. RFC 8259, OWASP ASVS V5."
    )

    # Expected Result 3: Response body is valid JSON
    assert is_valid_json(response.text), (
        "Response is not valid JSON. RFC 8259 compliance failed."
    )

# Optionally, add further schema checks in future (reference 'expected_response_schema' metadata once available).
