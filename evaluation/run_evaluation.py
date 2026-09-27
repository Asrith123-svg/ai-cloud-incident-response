import json
import os
import sys
import time

# --------------------------------------------------
# Project configuration
# --------------------------------------------------

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.insert(0, PROJECT_ROOT)

from app.rag import (
    load_runbooks,
    create_embeddings,
    create_faiss_index,
    search_runbooks
)


DATASET_PATH = os.path.join(
    PROJECT_ROOT,
    "evaluation",
    "evaluation_dataset.json"
)

RESULTS_PATH = os.path.join(
    PROJECT_ROOT,
    "evaluation",
    "evaluation_results.json"
)


# --------------------------------------------------
# Load evaluation dataset
# --------------------------------------------------

def load_dataset():

    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8-sig"
    ) as file:

        return json.load(file)


# --------------------------------------------------
# Main evaluation
# --------------------------------------------------

def evaluate():

    print("=" * 70)
    print("AI CLOUD INCIDENT RESPONSE - RAG EVALUATION")
    print("=" * 70)

    # --------------------------------------------------
    # 1. Load dataset
    # --------------------------------------------------

    dataset = load_dataset()

    print(
        f"\nLoaded evaluation incidents: "
        f"{len(dataset)}"
    )

    # --------------------------------------------------
    # 2. Load runbooks
    # --------------------------------------------------

    print("\nLoading runbooks...")

    chunks = load_runbooks()

    print(
        f"Loaded runbook chunks: "
        f"{len(chunks)}"
    )

    if not chunks:

        print(
            "\nERROR: No runbook chunks found."
        )

        return

    # --------------------------------------------------
    # 3. Create embeddings
    # --------------------------------------------------

    print("\nCreating embeddings...")

    embeddings = create_embeddings(
        chunks
    )

    print(
        f"Embedding shape: "
        f"{embeddings.shape}"
    )

    # --------------------------------------------------
    # 4. Create FAISS index
    # --------------------------------------------------

    print("\nCreating FAISS index...")

    index = create_faiss_index(
        embeddings
    )

    print(
        f"FAISS vectors: "
        f"{index.ntotal}"
    )

    # --------------------------------------------------
    # 5. Evaluate each incident
    # --------------------------------------------------

    print("\nStarting evaluation...")

    results = []

    retrieval_correct = 0

    total_retrieval_time = 0.0

    for number, incident in enumerate(
        dataset,
        start=1
    ):

        incident_id = incident[
            "incident_id"
        ]

        expected_runbook = incident[
            "expected_runbook"
        ]

        # Combine incident logs into query
        query = " ".join(
            incident["logs"]
        )

        print("\n" + "-" * 70)

        print(
            f"[{number}/{len(dataset)}] "
            f"{incident_id}"
        )

        print(
            f"Type: {incident['type']}"
        )

        print(
            f"Expected runbook: "
            f"{expected_runbook}"
        )

        # --------------------------------------------------
        # Measure retrieval time
        # --------------------------------------------------

        start_time = time.perf_counter()

        retrieved = search_runbooks(
            query,
            index,
            chunks,
            top_k=3
        )

        elapsed = (
            time.perf_counter()
            - start_time
        )

        total_retrieval_time += elapsed

        # --------------------------------------------------
        # Extract retrieved runbooks
        # --------------------------------------------------

        retrieved_runbooks = []

        for result in retrieved:

            source = result.get(
                "source",
                ""
            )

            if source:

                if source not in retrieved_runbooks:

                    retrieved_runbooks.append(
                        source
                    )

        # --------------------------------------------------
        # Check retrieval
        # --------------------------------------------------

        retrieval_match = (
            expected_runbook
            in retrieved_runbooks
        )

        if retrieval_match:

            retrieval_correct += 1

        result = {

            "incident_id":
                incident_id,

            "type":
                incident["type"],

            "expected_runbook":
                expected_runbook,

            "retrieved_runbooks":
                retrieved_runbooks,

            "retrieval_correct":
                retrieval_match,

            "retrieval_time_seconds":
                round(
                    elapsed,
                    4
                )
        }

        results.append(result)

        print(
            f"Retrieved: "
            f"{retrieved_runbooks}"
        )

        print(
            f"Result: "
            f"{'PASS' if retrieval_match else 'FAIL'}"
        )

        print(
            f"Retrieval time: "
            f"{elapsed:.4f} seconds"
        )

    # --------------------------------------------------
    # 6. Calculate metrics
    # --------------------------------------------------

    total_incidents = len(
        dataset
    )

    retrieval_incorrect = (
        total_incidents
        - retrieval_correct
    )

    retrieval_accuracy = (
        retrieval_correct
        / total_incidents
        * 100
        if total_incidents
        else 0
    )

    average_retrieval_time = (
        total_retrieval_time
        / total_incidents
        if total_incidents
        else 0
    )

    # --------------------------------------------------
    # 7. Build evaluation report
    # --------------------------------------------------

    evaluation = {

        "evaluation_summary": {

            "total_incidents":
                total_incidents,

            "retrieval_correct":
                retrieval_correct,

            "retrieval_incorrect":
                retrieval_incorrect,

            "retrieval_accuracy_percent":
                round(
                    retrieval_accuracy,
                    2
                ),

            "average_retrieval_time_seconds":
                round(
                    average_retrieval_time,
                    4
                )
        },

        "results":
            results
    }

    # --------------------------------------------------
    # 8. Save results
    # --------------------------------------------------

    with open(
        RESULTS_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            evaluation,
            file,
            indent=4
        )

    # --------------------------------------------------
    # 9. Display final results
    # --------------------------------------------------

    print("\n")

    print("=" * 70)
    print("EVALUATION COMPLETE")
    print("=" * 70)

    print(
        f"\nTotal incidents: "
        f"{total_incidents}"
    )

    print(
        f"Correct retrievals: "
        f"{retrieval_correct}"
    )

    print(
        f"Incorrect retrievals: "
        f"{retrieval_incorrect}"
    )

    print(
        f"Retrieval accuracy: "
        f"{retrieval_accuracy:.2f}%"
    )

    print(
        f"Average retrieval time: "
        f"{average_retrieval_time:.4f} seconds"
    )

    print(
        "\nResults saved to:"
    )

    print(
        RESULTS_PATH
    )

    print("\n" + "=" * 70)


# --------------------------------------------------
# Run
# --------------------------------------------------

if __name__ == "__main__":

    evaluate()
