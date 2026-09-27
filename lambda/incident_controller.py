import json
import boto3
from datetime import datetime, timezone


# ============================================================
# AWS CLIENTS
# ============================================================

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
sns = boto3.client("sns")


# ============================================================
# CONFIGURATION
# ============================================================

BUCKET_NAME = "ai-cloud-incident-response-784004375519"
TABLE_NAME = "AIIncidentHistory"
SNS_TOPIC_ARN = "arn:aws:sns:ap-south-1:784004375519:AIIncidentAlerts"

table = dynamodb.Table(TABLE_NAME)


# ============================================================
# RUNBOOK MAPPING
# ============================================================

RUNBOOK_MAP = {
    "AIIncident-PaymentAPI-DatabaseFailure": "database_failure.md"
}


# ============================================================
# REMEDIATION MAPPING
# ============================================================

REMEDIATION_MAP = {
    "AIIncident-PaymentAPI-DatabaseFailure": "CHECK_CONNECTION_POOL"
}


# ============================================================
# LAMBDA HANDLER
# ============================================================

def lambda_handler(event, context):

    print("=" * 70)
    print("AI INCIDENT CONTROLLER")
    print("=" * 70)

    print("\nReceived EventBridge event:")
    print(json.dumps(event, indent=2, default=str))


    # --------------------------------------------------------
    # Extract alarm information
    # --------------------------------------------------------

    detail = event.get("detail", {})

    alarm_name = detail.get(
        "alarmName",
        "UNKNOWN_ALARM"
    )

    alarm_state = detail.get(
        "state",
        {}
    ).get(
        "value",
        "UNKNOWN"
    )

    alarm_reason = detail.get(
        "state",
        {}
    ).get(
        "reason",
        "No reason provided"
    )


    print("\nAlarm name:")
    print(alarm_name)

    print("\nAlarm state:")
    print(alarm_state)

    print("\nAlarm reason:")
    print(alarm_reason)


    # --------------------------------------------------------
    # Generate incident ID
    # --------------------------------------------------------

    incident_id = (
        "INC-" +
        datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    )


    print("\nGenerated incident ID:")
    print(incident_id)


    # --------------------------------------------------------
    # Identify service
    # --------------------------------------------------------

    service = "payment-api"


    # --------------------------------------------------------
    # Retrieve runbook
    # --------------------------------------------------------

    runbook_file = RUNBOOK_MAP.get(
        alarm_name
    )


    if runbook_file is None:

        print("\nNo runbook mapping found.")

        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "No runbook mapping found",
                "alarm_name": alarm_name
            })
        }


    print("\nRunbook:")
    print(runbook_file)


    try:

        response = s3.get_object(
            Bucket=BUCKET_NAME,
            Key=f"runbooks/{runbook_file}"
        )

        runbook_content = response[
            "Body"
        ].read().decode("utf-8")


        print("\nRunbook retrieved successfully.")


    except Exception as e:

        print("\nFailed to retrieve runbook:")
        print(str(e))

        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Failed to retrieve runbook",
                "error": str(e)
            })
        }


    # --------------------------------------------------------
    # Build AI analysis prompt
    # --------------------------------------------------------

    analysis_prompt = f"""
You are an AI production incident analysis assistant.

Analyze the following production incident.

Incident ID:
{incident_id}

Service:
{service}

Alarm:
{alarm_name}

Alarm State:
{alarm_state}

Alarm Reason:
{alarm_reason}

Runbook:
{runbook_content}

Provide:

1. Severity
2. Root cause
3. Confidence
4. Evidence
5. Recommended action

Do not invent evidence.

The analysis will be performed by a separate local AI worker.
"""


    print("\nAI analysis prompt created.")


    # --------------------------------------------------------
    # Recommended remediation
    # --------------------------------------------------------

    recommended_action = REMEDIATION_MAP.get(
        alarm_name,
        "INVESTIGATE_DATABASE_CONNECTIONS"
    )


    # --------------------------------------------------------
    # Create DynamoDB incident record
    # --------------------------------------------------------

    incident_record = {

        "incident_id": incident_id,

        "service": service,

        "alarm_name": alarm_name,

        "alarm_state": alarm_state,

        "alarm_reason": alarm_reason,

        "runbook": runbook_file,

        "analysis_prompt": analysis_prompt,

        "recommended_action": recommended_action,

        "status": "ANALYSIS_PENDING",

        "created_at": datetime.now(
            timezone.utc
        ).isoformat()

    }


    print("\nSaving incident to DynamoDB...")

    try:

        table.put_item(
            Item=incident_record
        )

        print(
            "Incident saved successfully."
        )

    except Exception as e:

        print(
            "Failed to save incident:"
        )

        print(str(e))

        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Failed to save incident",
                "error": str(e)
            })
        }


    # --------------------------------------------------------
    # Send SNS notification
    # --------------------------------------------------------

    message = f"""
AI Cloud Incident Detected

Incident ID:
{incident_id}

Service:
{service}

Alarm:
{alarm_name}

State:
{alarm_state}

Status:
ANALYSIS_PENDING

The incident has been detected and stored.
The local AI worker will perform RAG-based root-cause analysis.
"""


    try:

        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="AI Incident Detected",
            Message=message
        )

        print(
            "SNS notification sent successfully."
        )

    except Exception as e:

        print(
            "SNS notification failed:"
        )

        print(str(e))


    # --------------------------------------------------------
    # Final response
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("INCIDENT CREATED")
    print("=" * 70)

    print(
        f"Incident ID: {incident_id}"
    )

    print(
        "Status: ANALYSIS_PENDING"
    )

    print(
        f"Recommended action: {recommended_action}"
    )


    return {

        "statusCode": 200,

        "body": json.dumps({

            "message": "Incident created successfully",

            "incident_id": incident_id,

            "status": "ANALYSIS_PENDING",

            "recommended_action":
                recommended_action

        })

    }