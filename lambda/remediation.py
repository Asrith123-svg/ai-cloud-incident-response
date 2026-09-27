import json
from datetime import datetime, timezone


def lambda_handler(event, context):

    print("=" * 60)
    print("AI INCIDENT REMEDIATION")
    print("=" * 60)

    print("\nReceived approval event:")
    print(json.dumps(event, indent=2, default=str))

    incident_id = event.get(
        "incident_id",
        "UNKNOWN"
    )

    action = event.get(
        "action",
        "UNKNOWN"
    )

    # ---------------------------------------------------------
    # Only allow explicitly predefined actions
    # ---------------------------------------------------------

    allowed_actions = [
        "INVESTIGATE_DATABASE_CONNECTIONS",
        "CHECK_CONNECTION_POOL"
    ]

    if action not in allowed_actions:

        print("\nAction rejected.")

        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Action is not allowed",
                "incident_id": incident_id,
                "action": action
            })
        }

    # ---------------------------------------------------------
    # Execute safe remediation
    # ---------------------------------------------------------

    print("\nApproved action:")
    print(action)

    print("\nExecuting controlled remediation...")

    result = {
        "incident_id": incident_id,
        "action": action,
        "status": "EXECUTED",
        "executed_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "message": "Controlled remediation executed successfully"
    }

    print("\nRemediation result:")
    print(json.dumps(result, indent=2))

    return {
        "statusCode": 200,
        "body": json.dumps(result)
    }