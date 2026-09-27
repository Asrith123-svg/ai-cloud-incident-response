import json
import boto3

lambda_client = boto3.client("lambda")

APPROVAL_FUNCTION = "AIIncidentApproval"


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(body)
    }


def lambda_handler(event, context):

    print("=" * 60)
    print("AI INCIDENT API HANDLER")
    print("=" * 60)

    print("\nReceived API Gateway event:")
    print(json.dumps(event, indent=2, default=str))

    # Get HTTP method and path
    request_context = event.get("requestContext", {})
    http = request_context.get("http", {})

    method = http.get("method", "")
    path = event.get("rawPath", "")

    print(f"\nMethod: {method}")
    print(f"Path: {path}")

    if method != "POST":
        return response(
            405,
            {
                "message": "Only POST requests are allowed"
            }
        )

    # Determine decision from endpoint
    if path.endswith("/approve"):
        decision = "APPROVE"

    elif path.endswith("/reject"):
        decision = "REJECT"

    else:
        return response(
            404,
            {
                "message": "Unknown endpoint"
            }
        )

    # Parse request body
    body = event.get("body")

    if not body:
        return response(
            400,
            {
                "message": "Request body is required"
            }
        )

    try:
        body_data = json.loads(body)
    except json.JSONDecodeError:
        return response(
            400,
            {
                "message": "Request body must be valid JSON"
            }
        )

    incident_id = body_data.get("incident_id")

    if not incident_id:
        return response(
            400,
            {
                "message": "incident_id is required"
            }
        )

    print(f"\nIncident ID: {incident_id}")
    print(f"Decision: {decision}")

    # Build event for existing Approval Lambda
    approval_event = {
        "incident_id": incident_id,
        "decision": decision
    }

    print("\nInvoking Approval Lambda...")

    result = lambda_client.invoke(
        FunctionName=APPROVAL_FUNCTION,
        InvocationType="RequestResponse",
        Payload=json.dumps(approval_event).encode("utf-8")
    )

    response_payload = result["Payload"].read().decode("utf-8")

    print("\nApproval Lambda response:")
    print(response_payload)

    try:
        approval_result = json.loads(response_payload)
    except json.JSONDecodeError:
        approval_result = {
            "raw_response": response_payload
        }

    return response(
        200,
        {
            "message": "Approval request processed",
            "incident_id": incident_id,
            "decision": decision,
            "approval_lambda_response": approval_result
        }
    )