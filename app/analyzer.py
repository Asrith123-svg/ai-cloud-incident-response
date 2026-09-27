import json
from pathlib import Path

from rag import load_runbooks, create_embeddings, create_faiss_index, search_runbooks


# --------------------------------------------------
# Configuration
# --------------------------------------------------

INCIDENT_FILE = (
    Path(__file__).parent.parent
    / "incidents"
    / "test_incidents.json"
)


# --------------------------------------------------
# Load Incidents
# --------------------------------------------------

def load_incidents():
    """
    Load test incidents from JSON.
    """

    with open(INCIDENT_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


# --------------------------------------------------
# Convert Incident to Search Query
# --------------------------------------------------

def incident_to_query(incident):
    """
    Convert incident information into text
    that can be searched using RAG.
    """

    logs = "\n".join(incident["logs"])

    query = f"""
Service: {incident["service"]}

CPU: {incident["cpu"]}%
Memory: {incident["memory"]}%
Error Rate: {incident["error_rate"]}%
Latency: {incident["latency_ms"]} ms

Logs:
{logs}
"""

    return query.strip()


# --------------------------------------------------
# Build AI Prompt
# --------------------------------------------------

def build_prompt(incident, retrieved_context):
    """
    Build the prompt that will eventually be
    sent to Amazon Bedrock.
    """

    context_text = "\n\n".join(
        [
            f"Source: {item['source']}\n{item['text']}"
            for item in retrieved_context
        ]
    )

    prompt = f"""
You are an AI Cloud Incident Response Assistant.

Your task is to analyze a production incident using
the incident evidence and the retrieved operational
runbook information.

INCIDENT
--------

Incident ID:
{incident["incident_id"]}

Service:
{incident["service"]}

CPU:
{incident["cpu"]}%

Memory:
{incident["memory"]}%

Error Rate:
{incident["error_rate"]}%

Latency:
{incident["latency_ms"]} ms

Logs:
{chr(10).join(incident["logs"])}


RETRIEVED OPERATIONAL KNOWLEDGE
--------------------------------

{context_text}


TASK
----

Analyze the incident and determine:

1. Severity
2. Most likely root cause
3. Evidence supporting the root cause
4. Confidence level
5. Recommended actions

Do not invent evidence that is not present
in the incident or retrieved operational knowledge.

Return the result as JSON with this structure:

{{
    "severity": "...",
    "root_cause": "...",
    "confidence": 0.0,
    "evidence": [],
    "recommendations": []
}}
"""

    return prompt.strip()


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    print("\n" + "=" * 60)
    print("AI INCIDENT ANALYZER")
    print("=" * 60)

    # Load incidents
    incidents = load_incidents()

    # Select our database incident
    incident = incidents[1]

    print("\nIncident selected:")
    print(incident["incident_id"])

    # Create RAG index
    print("\nBuilding RAG index...")

    chunks = load_runbooks()

    embeddings = create_embeddings(chunks)

    index = create_faiss_index(embeddings)

    print(f"Loaded {len(chunks)} chunks.")

    # Convert incident into search query
    query = incident_to_query(incident)

    print("\nSearching relevant knowledge...")

    retrieved_context = search_runbooks(
        query,
        index,
        chunks,
        top_k=3
    )

    # Build prompt
    prompt = build_prompt(
        incident,
        retrieved_context
    )

    print("\n" + "=" * 60)
    print("PROMPT THAT WILL BE SENT TO THE LLM")
    print("=" * 60)

    print(prompt)

    print("\n" + "=" * 60)
    print("ANALYZER READY")
    print("=" * 60)


if __name__ == "__main__":
    main()
    