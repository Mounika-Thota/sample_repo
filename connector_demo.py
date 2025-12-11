#!/usr/bin/env python3
"""
Example script demonstrating the connector system usage.
This shows how to configure and use the Jira connector.
"""

from typing import Any

import requests

# Configuration
BASE_URL = "http://localhost:8000"  # Adjust to your FastAPI server URL
PROJECT_ID = "example-project-id"
USER_TOKEN = "your-auth-token"  # Replace with actual auth token

# Sample Jira configuration using the new unified config structure
JIRA_CONNECTOR_ID = "jira-connector-id"  # Replace with actual global connector ID

JIRA_CONFIG = {
    "connector_id": JIRA_CONNECTOR_ID,
    "connector_name": "Primary Jira",
    "config": {
        "connection": {
            "base_url": "https://your-domain.atlassian.net",
            "auth_type": "api_token",
            "auth_config": {
                "email": "your-email@company.com",
                "api_token": "ATATT3xFf...",  # Replace with actual API token
            },
        },
        "project": {
            "project_key": "DEV",
            "default_assignee": "user123",
            "default_labels": ["generated", "user-story"],
            "field_mappings": {
                "story_points": "customfield_10016",
                "epic_link": "customfield_10014",
            },
        },
        "additional": {
            "default_priority": "Medium",
            "issue_type": "Story",
            "workflow_settings": {"auto_transition": True},
        },
    },
}


def make_request(method: str, endpoint: str, data: dict[Any, Any] = None) -> dict[Any, Any]:
    """Make HTTP request to the API"""
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {USER_TOKEN}"}

    url = f"{BASE_URL}{endpoint}"

    if method.upper() == "GET":
        response = requests.get(url, headers=headers)
    elif method.upper() == "POST":
        response = requests.post(url, headers=headers, json=data)
    else:
        raise ValueError(f"Unsupported method: {method}")

    response.raise_for_status()
    return response.json()


def main():
    """Demonstrate the connector system workflow"""

    print("🚀 Connector System Demo")
    print("=" * 40)

    try:
        # 1. List global connectors
        print("\n1. Listing global connectors...")
        global_connectors = make_request("GET", "/connectors")
        connector_names = [c["name"] for c in global_connectors]
        print(f"   Global connectors: {connector_names}")

        # 2. Create a project connector configuration
        print("\n2. Creating project connector configuration (Jira example)...")
        project_connector_payload = {
            "connector_id": JIRA_CONFIG["connector_id"],
            "connector_name": JIRA_CONFIG["connector_name"],
            "config": JIRA_CONFIG["config"],
        }
        created = make_request(
            "POST", f"/projects/{PROJECT_ID}/datasources", project_connector_payload
        )
        print(f"   Created project connector: {created['connector_name']} (id={created['id']})")

        # 3. List project connectors
        print("\n3. Listing project connectors...")
        project_conns = make_request("GET", f"/projects/{PROJECT_ID}/datasources")
        names = [c["connector_name"] for c in project_conns]
        print(f"   Project connectors: {names}")

        # 4. Retrieve single connector
        print("\n4. Retrieving single connector...")
        single = make_request("GET", f"/projects/{PROJECT_ID}/datasources/{created['id']}")
        print(f"   Retrieved: {single['connector_name']} (type={single.get('connector_type')})")

        # 5. Test connection
        print("\n5. Testing connection...")
        test_result = make_request(
            "POST", f"/projects/{PROJECT_ID}/datasources/{created['id']}/test-connection"
        )
        print(f"   Connection test: {test_result['message']} (Success: {test_result['success']})")

        # 6. Validate configuration (example of validation endpoint)
        print("\n6. Validating configuration structure...")
        validation_payload = {
            "connector_id": JIRA_CONFIG["connector_id"],
            "config": JIRA_CONFIG["config"],
        }
        validation_result = make_request(
            "POST", f"/projects/{PROJECT_ID}/datasources/validate-config", validation_payload
        )
        print(f"   Config validation: {'Valid' if validation_result['valid'] else 'Invalid'}")
        if validation_result.get("errors"):
            print(f"   Validation errors: {validation_result['errors']}")

        # 7. Get connector configuration requirements
        print("\n7. Getting connector configuration requirements...")
        requirements = make_request(
            "GET", f"/connectors/{JIRA_CONFIG['connector_id']}/config-requirements"
        )
        print(f"   Supported auth types: {requirements['supported_auth_types']}")
        print(
            f"   Required config sections: {list(requirements['config_schema']['properties'].keys())}"
        )

        # 8. Update connector (rename and config change)
        print("\n8. Updating connector...")
        updated_config = JIRA_CONFIG["config"].copy()
        updated_config["project"]["project_key"] = "UPDATED"
        update_payload = {"connector_name": "Renamed Jira", "config": updated_config}
        updated = make_request(
            "PUT", f"/projects/{PROJECT_ID}/datasources/{created['id']}", update_payload
        )
        print(f"   Updated name: {updated['connector_name']}")

        # 9. Soft delete connector
        print("\n9. Deleting connector (soft)...")
        deleted = make_request("DELETE", f"/projects/{PROJECT_ID}/datasources/{created['id']}")
        print(f"   Deleted: {deleted['deleted']}")

        print("\n✅ Demo completed successfully (project-centric connectors)!\n")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ API request failed: {e}")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")


if __name__ == "__main__":
    # Check if configuration is provided
    if JIRA_CONFIG["config"]["connection"]["auth_config"]["api_token"] == "ATATT3xFf...":
        print(
            "⚠️  Please update the JIRA_CONFIG with your actual Jira credentials before running this demo."
        )
        print("\nRequired configuration:")
        print("- config.connection.base_url: Your Jira instance URL")
        print("- config.connection.auth_config.email: Your Jira email")
        print("- config.connection.auth_config.api_token: Your Jira API token")
        print("- config.project.project_key: Target Jira project key")
        exit(1)

    main()
