import json


def build_analysis_prompt(incident, runbook_context):
    """
    Build a structured prompt for AI-based
    incident root-cause analysis.
    """

    prompt = f"""
You are an AI cloud incident response assistant.

Analyze the following production incident using
ONLY the incident information and runbook evidence
provided below.

INCIDENT INFORMATION
--------------------
Incident ID: {incident.get("incident_id")}
Alarm Name: {incident.get("alarm_name")}
Alarm State: {incident.get("alarm_state")}
Alarm Reason: {incident.get("alarm_reason")}
Service: payment-api

RUNBOOK EVIDENCE
----------------
{runbook_context}

ANALYSIS REQUIREMENTS
---------------------
Determine:

1. Severity
2. Most likely root cause
3. Evidence supporting the root cause
4. Confidence score from 0.0 to 1.0
5. Recommended investigation/recovery actions

Return ONLY valid JSON using this structure:

{{
    "severity": "LOW | MEDIUM | HIGH | CRITICAL",
    "root_cause": "string",
    "confidence": 0.0,
    "evidence": [
        "string"
    ],
    "recommendations": [
        "string"
    ]
}}
"""

    return prompt


def analyze_incident(incident, runbook_context):
    """
    Prepare the incident analysis request.
    """

    prompt = build_analysis_prompt(
        incident,
        runbook_context
    )

    print("=" * 60)
    print("AI INCIDENT ANALYSIS PROMPT")
    print("=" * 60)

    print(prompt)

    return {
        "status": "READY_FOR_LLM",
        "prompt": prompt
    }


if __name__ == "__main__":

    test_incident = {
        "incident_id": "INC-20260923112557",
        "alarm_name": "AIIncident-PaymentAPI-DatabaseFailure",
        "alarm_state": "ALARM",
        "alarm_reason": "Database connection failures detected"
    }

    test_runbook = """
Database connection timeout
Connection pool exhaustion
Failed database queries

Possible causes:
- Database unavailable
- Network connectivity problems
- Connection pool exhaustion
- Database overload
"""

    result = analyze_incident(
        test_incident,
        test_runbook
    )

    print("\nResult:")
    print(json.dumps(result, indent=2))