import json
import time
import urllib.request
import urllib.error

from decimal import Decimal
from datetime import datetime, timezone

import boto3

from rag import (
    load_runbooks,
    create_embeddings,
    create_faiss_index,
    search_runbooks
)


# ============================================================
# CONFIGURATION
# ============================================================

AWS_REGION = "ap-south-1"

DYNAMODB_TABLE = "AIIncidentHistory"

OLLAMA_URL = "http://localhost:11434/api/generate"

OLLAMA_MODEL = "llama3.2:3b"

POLL_INTERVAL = 10


# ============================================================
# AWS CLIENTS
# ============================================================

dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION
)

table = dynamodb.Table(
    DYNAMODB_TABLE
)


# ============================================================
# RAG INITIALIZATION
# ============================================================

print("=" * 70)
print("INITIALIZING AI INCIDENT ANALYSIS WORKER")
print("=" * 70)

print("\nLoading runbooks...")

chunks = load_runbooks()

print(
    f"Loaded {len(chunks)} runbook chunks."
)

print("\nCreating embeddings...")

embeddings = create_embeddings(
    chunks
)

print(
    f"Embedding shape: {embeddings.shape}"
)

print("\nCreating FAISS index...")

index = create_faiss_index(
    embeddings
)

print("FAISS index ready.")


# ============================================================
# CONVERT PYTHON TYPES TO DYNAMODB TYPES
# ============================================================

def convert_to_dynamodb(value):

    # Float -> Decimal
    if isinstance(value, float):

        return Decimal(
            str(value)
        )

    # Integer
    if isinstance(value, int):

        return value

    # Dictionary
    if isinstance(value, dict):

        return {
            key: convert_to_dynamodb(
                item
            )
            for key, item in value.items()
        }

    # List
    if isinstance(value, list):

        return [
            convert_to_dynamodb(item)
            for item in value
        ]

    # Tuple
    if isinstance(value, tuple):

        return [
            convert_to_dynamodb(item)
            for item in value
        ]

    return value


# ============================================================
# GET PENDING INCIDENTS
# ============================================================

def get_pending_incidents():

    response = table.scan()

    incidents = response.get(
        "Items",
        []
    )

    pending = []

    for incident in incidents:

        status = incident.get(
            "status",
            ""
        )

        if status in [
            "ANALYSIS_PENDING",
            "ANALYSIS_READY"
        ]:

            pending.append(
                incident
            )

    return pending


# ============================================================
# BUILD RAG QUERY
# ============================================================

def build_rag_query(
    incident
):

    alarm_name = incident.get(
        "alarm_name",
        ""
    )

    alarm_reason = incident.get(
        "alarm_reason",
        ""
    )

    service = incident.get(
        "service",
        ""
    )

    analysis_prompt = incident.get(
        "analysis_prompt",
        ""
    )

    query = f"""
Alarm:
{alarm_name}

Reason:
{alarm_reason}

Service:
{service}

Incident details:
{analysis_prompt}
"""

    return query.strip()


# ============================================================
# BUILD AI PROMPT
# ============================================================

def build_ai_prompt(
    incident,
    retrieved_context
):

    incident_id = incident.get(
        "incident_id",
        "UNKNOWN"
    )

    alarm_name = incident.get(
        "alarm_name",
        "UNKNOWN"
    )

    alarm_reason = incident.get(
        "alarm_reason",
        "UNKNOWN"
    )

    service = incident.get(
        "service",
        "UNKNOWN"
    )

    analysis_prompt = incident.get(
        "analysis_prompt",
        ""
    )


    context_text = "\n\n".join(
        [
            f"Source: {item['source']}\n"
            f"{item['text']}"
            for item in retrieved_context
        ]
    )


    prompt = f"""
You are an AI cloud incident analysis assistant.

Analyze the production incident using ONLY the
incident information and retrieved runbook evidence.

Do not invent facts.

Do not invent timestamps.

Do not invent metrics.

Do not invent configuration values.

Do not assume evidence that is not provided.

Do not generate AWS CLI commands.

Do not generate destructive actions.

Return ONLY valid JSON.

Use exactly this structure:

{{
  "severity": "LOW | MEDIUM | HIGH | CRITICAL",
  "root_cause": "short explanation",
  "confidence": 0.0,
  "evidence": [],
  "recommendations": []
}}

Rules:

1. severity must be LOW, MEDIUM, HIGH, or CRITICAL.

2. confidence must be between 0 and 1.

3. Evidence must come only from the incident
   or retrieved runbook.

4. Recommendations must be safe.

5. Do not generate arbitrary AWS commands.

6. Do not generate destructive actions.

7. Return JSON only.

Incident ID:
{incident_id}

Service:
{service}

Alarm:
{alarm_name}

Alarm reason:
{alarm_reason}

Incident information:
{analysis_prompt}

Retrieved runbook evidence:
{context_text}
"""

    return prompt.strip()


# ============================================================
# CALL OLLAMA
# ============================================================

def call_ollama(
    prompt
):

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.1
        }
    }


    request = urllib.request.Request(

        OLLAMA_URL,

        data=json.dumps(
            payload
        ).encode("utf-8"),

        headers={
            "Content-Type":
                "application/json"
        },

        method="POST"
    )


    try:

        with urllib.request.urlopen(
            request,
            timeout=120
        ) as response:

            response_body = (
                response
                .read()
                .decode("utf-8")
            )

            result = json.loads(
                response_body
            )

            return result.get(
                "response",
                ""
            )


    except urllib.error.URLError as error:

        raise RuntimeError(
            f"Could not connect to Ollama: {error}"
        )


# ============================================================
# VALIDATE AI RESPONSE
# ============================================================

def validate_ai_response(
    response_text
):

    try:

        analysis = json.loads(
            response_text
        )

    except json.JSONDecodeError as error:

        raise ValueError(
            f"Ollama returned invalid JSON: {error}"
        )


    required_fields = [
        "severity",
        "root_cause",
        "confidence",
        "evidence",
        "recommendations"
    ]


    for field in required_fields:

        if field not in analysis:

            raise ValueError(
                f"Missing required field: {field}"
            )


    valid_severities = [
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL"
    ]


    if analysis["severity"] not in valid_severities:

        raise ValueError(
            "Invalid severity returned by AI"
        )


    confidence = analysis[
        "confidence"
    ]


    if not isinstance(
        confidence,
        (int, float)
    ):

        raise ValueError(
            "Confidence must be numeric"
        )


    if not 0 <= confidence <= 1:

        raise ValueError(
            "Confidence must be between 0 and 1"
        )


    if not isinstance(
        analysis["evidence"],
        list
    ):

        raise ValueError(
            "Evidence must be a list"
        )


    if not isinstance(
        analysis["recommendations"],
        list
    ):

        raise ValueError(
            "Recommendations must be a list"
        )


    return analysis


# ============================================================
# SAVE ANALYSIS TO DYNAMODB
# ============================================================

def save_analysis(
    incident_id,
    analysis
):

    analysis_time = (
        datetime.now(
            timezone.utc
        ).isoformat()
    )


    # Convert the COMPLETE AI result.
    #
    # This is important because:
    #
    # analysis
    # └── confidence = 0.8
    #
    # is also stored inside ai_analysis.
    #
    # DynamoDB does not accept Python floats.
    dynamodb_analysis = (
        convert_to_dynamodb(
            analysis
        )
    )


    confidence = (
        convert_to_dynamodb(
            analysis["confidence"]
        )
    )


    table.update_item(

        Key={
            "incident_id":
                incident_id
        },

        UpdateExpression="""
            SET
                ai_analysis = :ai_analysis,
                severity = :severity,
                root_cause = :root_cause,
                confidence = :confidence,
                evidence = :evidence,
                recommendations = :recommendations,
                analysis_time = :analysis_time,
                #status = :status
        """,

        ExpressionAttributeNames={
            "#status": "status"
        },

        ExpressionAttributeValues={

            ":ai_analysis":
                dynamodb_analysis,

            ":severity":
                analysis["severity"],

            ":root_cause":
                analysis["root_cause"],

            ":confidence":
                confidence,

            ":evidence":
                analysis["evidence"],

            ":recommendations":
                analysis["recommendations"],

            ":analysis_time":
                analysis_time,

            ":status":
                "AWAITING_APPROVAL"
        }
    )


# ============================================================
# PROCESS INCIDENT
# ============================================================

def process_incident(
    incident
):

    incident_id = incident.get(
        "incident_id",
        "UNKNOWN"
    )


    print("\n")
    print("=" * 70)
    print(
        f"PROCESSING INCIDENT: {incident_id}"
    )
    print("=" * 70)


    # --------------------------------------------------------
    # 1. RAG
    # --------------------------------------------------------

    print(
        "\n1. Retrieving relevant runbook context..."
    )


    query = build_rag_query(
        incident
    )


    retrieved_context = search_runbooks(
        query,
        index,
        chunks,
        top_k=3
    )


    print(
        f"Retrieved {len(retrieved_context)} "
        f"runbook sections."
    )


    for item in retrieved_context:

        print(
            f"  - {item['source']}"
        )


    # --------------------------------------------------------
    # 2. PROMPT
    # --------------------------------------------------------

    print(
        "\n2. Building AI prompt..."
    )


    prompt = build_ai_prompt(
        incident,
        retrieved_context
    )


    print(
        "Prompt created."
    )


    # --------------------------------------------------------
    # 3. OLLAMA
    # --------------------------------------------------------

    print(
        "\n3. Sending incident to Ollama..."
    )


    response_text = call_ollama(
        prompt
    )


    print(
        "\nOllama response:"
    )

    print(
        response_text
    )


    # --------------------------------------------------------
    # 4. VALIDATION
    # --------------------------------------------------------

    print(
        "\n4. Validating AI response..."
    )


    analysis = validate_ai_response(
        response_text
    )


    print(
        "\nValidated analysis:"
    )


    print(
        json.dumps(
            analysis,
            indent=2
        )
    )


    # --------------------------------------------------------
    # 5. DYNAMODB
    # --------------------------------------------------------

    print(
        "\n5. Saving analysis to DynamoDB..."
    )


    save_analysis(
        incident_id,
        analysis
    )


    print(
        "\nAnalysis saved successfully."
    )


    print(
        "Incident status: "
        "AWAITING_APPROVAL"
    )


# ============================================================
# MAIN LOOP
# ============================================================

def main():

    print("\n")
    print("=" * 70)
    print(
        "AI INCIDENT ANALYSIS WORKER STARTED"
    )
    print("=" * 70)

    print(
        f"\nOllama model: {OLLAMA_MODEL}"
    )

    print(
        f"DynamoDB table: {DYNAMODB_TABLE}"
    )

    print(
        f"Polling every "
        f"{POLL_INTERVAL} seconds."
    )


    while True:

        try:

            print(
                "\nWaiting for incidents..."
            )


            incidents = (
                get_pending_incidents()
            )


            if not incidents:

                time.sleep(
                    POLL_INTERVAL
                )

                continue


            for incident in incidents:

                try:

                    process_incident(
                        incident
                    )

                except Exception as error:

                    print(
                        f"\nERROR processing "
                        f"{incident.get('incident_id', 'UNKNOWN')}:"
                    )

                    print(
                        str(error)
                    )


            time.sleep(
                POLL_INTERVAL
            )


        except KeyboardInterrupt:

            print(
                "\n\nAI Incident Analysis Worker stopped."
            )

            break


        except Exception as error:

            print(
                "\nWorker error:"
            )

            print(
                str(error)
            )

            time.sleep(
                POLL_INTERVAL
            )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()