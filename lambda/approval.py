import json
import boto3
from datetime import datetime, timezone


# =========================================================
# AWS CLIENTS
# =========================================================

dynamodb = boto3.resource("dynamodb")
lambda_client = boto3.client("lambda")


# =========================================================
# AWS RESOURCES
# =========================================================

TABLE_NAME = "AIIncidentHistory"

REMEDIATION_FUNCTION = "AIIncidentRemediation"


table = dynamodb.Table(TABLE_NAME)


# =========================================================
# LAMBDA HANDLER
# =========================================================

def lambda_handler(event, context):

    print("=" * 60)
    print("AI INCIDENT APPROVAL CONTROLLER")
    print("=" * 60)

    print("\nReceived event:")
    print(
        json.dumps(
            event,
            indent=2,
            default=str
        )
    )

    # -----------------------------------------------------
    # Get incident ID
    # -----------------------------------------------------

    incident_id = event.get(
        "incident_id"
    )

    if not incident_id:

        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "incident_id is required"
            })
        }


    # -----------------------------------------------------
    # Get approval decision
    # -----------------------------------------------------

    decision = event.get(
        "decision",
        ""
    ).upper()


    if decision not in [
        "APPROVE",
        "REJECT"
    ]:

        return {
            "statusCode": 400,
            "body": json.dumps({
                "message":
                    "decision must be APPROVE or REJECT"
            })
        }


    # -----------------------------------------------------
    # Get incident from DynamoDB
    # -----------------------------------------------------

    print(
        f"\nLooking up incident: {incident_id}"
    )

    response = table.get_item(
        Key={
            "incident_id": incident_id
        }
    )

    incident = response.get(
        "Item"
    )

    if not incident:

        return {
            "statusCode": 404,
            "body": json.dumps({
                "message":
                    "Incident not found",
                "incident_id":
                    incident_id
            })
        }


    # -----------------------------------------------------
    # Verify current incident status
    # -----------------------------------------------------

    current_status = incident.get(
        "status"
    )

    print(
        f"\nCurrent status: {current_status}"
    )

    if current_status != "AWAITING_APPROVAL":

        return {
            "statusCode": 409,
            "body": json.dumps({
                "message":
                    "Incident is not awaiting approval",
                "incident_id":
                    incident_id,
                "current_status":
                    current_status
            })
        }


    # =====================================================
    # REJECT
    # =====================================================

    if decision == "REJECT":

        table.update_item(

            Key={
                "incident_id":
                    incident_id
            },

            UpdateExpression="""
                SET #status = :status,
                    approval_decision = :decision,
                    approval_time = :time
            """,

            ExpressionAttributeNames={
                "#status":
                    "status"
            },

            ExpressionAttributeValues={
                ":status":
                    "REJECTED",

                ":decision":
                    "REJECT",

                ":time":
                    datetime.now(
                        timezone.utc
                    ).isoformat()
            }
        )

        print(
            "\nIncident rejected."
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message":
                    "Incident rejected",
                "incident_id":
                    incident_id,
                "status":
                    "REJECTED"
            })
        }


    # =====================================================
    # APPROVE
    # =====================================================

    recommended_action = incident.get(
        "recommended_action"
    )

    if not recommended_action:

        return {
            "statusCode": 400,
            "body": json.dumps({
                "message":
                    "No recommended remediation action found",
                "incident_id":
                    incident_id
            })
        }


    print(
        f"\nApproved remediation: "
        f"{recommended_action}"
    )


    # -----------------------------------------------------
    # Invoke remediation Lambda
    # -----------------------------------------------------

    remediation_event = {

        "incident_id":
            incident_id,

        "action":
            recommended_action
    }


    print(
        "\nInvoking remediation Lambda..."
    )


    response = lambda_client.invoke(

        FunctionName=
            REMEDIATION_FUNCTION,

        InvocationType=
            "RequestResponse",

        Payload=
            json.dumps(
                remediation_event
            ).encode("utf-8")
    )


    response_payload = response[
        "Payload"
    ].read().decode("utf-8")


    print(
        "\nRemediation response:"
    )

    print(
        response_payload
    )


    # -----------------------------------------------------
    # Update incident
    # -----------------------------------------------------

    table.update_item(

        Key={
            "incident_id":
                incident_id
        },

        UpdateExpression="""
            SET #status = :status,
                approval_decision = :decision,
                approval_time = :time,
                remediation_action = :action,
                remediation_result = :result
        """,

        ExpressionAttributeNames={
            "#status":
                "status"
        },

        ExpressionAttributeValues={

            ":status":
                "REMEDIATION_EXECUTED",

            ":decision":
                "APPROVE",

            ":time":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            ":action":
                recommended_action,

            ":result":
                response_payload
        }
    )


    print(
        "\nIncident updated successfully."
    )


    # =====================================================
    # RETURN
    # =====================================================

    return {

        "statusCode":
            200,

        "body":
            json.dumps({

                "message":
                    "Incident approved and remediation executed",

                "incident_id":
                    incident_id,

                "decision":
                    "APPROVE",

                "action":
                    recommended_action,

                "status":
                    "REMEDIATION_EXECUTED"
            })
    }