from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

# Location of the runbooks folder
RUNBOOK_DIR = Path(__file__).parent.parent / "runbooks"

# Embedding model
MODEL_NAME = "all-MiniLM-L6-v2"

# Number of results to retrieve
TOP_K = 3


# --------------------------------------------------
# 2. Load Embedding Model
# --------------------------------------------------

print("Loading embedding model...")

model = SentenceTransformer(MODEL_NAME)

print("Embedding model loaded.")


# --------------------------------------------------
# 3. Load Runbooks
# --------------------------------------------------

def load_runbooks():
    """
    Read all Markdown runbooks and split them
    into smaller sections/chunks.
    """

    chunks = []

    # Find every .md file inside runbooks/
    for file_path in RUNBOOK_DIR.glob("*.md"):

        # Read the file
        text = file_path.read_text(encoding="utf-8")

        # Split the document using Markdown headings
        sections = text.split("\n## ")

        for section in sections:

            section = section.strip()

            if not section:
                continue

            chunks.append({
                "text": section,
                "source": file_path.name
            })

    return chunks


# --------------------------------------------------
# 4. Create Embeddings
# --------------------------------------------------

def create_embeddings(chunks):
    """
    Convert each text chunk into a numerical vector.
    """

    texts = [chunk["text"] for chunk in chunks]

    embeddings = model.encode(
        texts,
        convert_to_numpy=True
    )

    return embeddings


# --------------------------------------------------
# 5. Create FAISS Index
# --------------------------------------------------

def create_faiss_index(embeddings):
    """
    Create a FAISS index and store the embeddings.
    """

    # Number of dimensions in each embedding
    dimension = embeddings.shape[1]

    # Create FAISS index using L2 distance
    index = faiss.IndexFlatL2(dimension)

    # Add our embeddings to the index
    index.add(embeddings)

    return index


# --------------------------------------------------
# 6. Search Relevant Runbooks
# --------------------------------------------------

def search_runbooks(query, index, chunks, top_k=TOP_K):
    """
    Search for the most relevant runbook chunks
    for a given incident/query.
    """

    # Convert the query into an embedding
    query_embedding = model.encode(
        [query],
        convert_to_numpy=True
    )

    # Search FAISS
    distances, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for i in indices[0]:

        # Ignore invalid indexes
        if i == -1:
            continue

        results.append({
            "source": chunks[i]["source"],
            "text": chunks[i]["text"]
        })

    return results


# --------------------------------------------------
# 7. Main Program
# --------------------------------------------------

def main():

    print("\n" + "=" * 60)
    print("AI CLOUD INCIDENT RESPONSE - RAG SYSTEM")
    print("=" * 60)

    # Step 1: Load runbooks
    print("\n[1] Loading runbooks...")

    chunks = load_runbooks()

    print(f"Loaded {len(chunks)} chunks.")

    if not chunks:
        print("ERROR: No runbooks found.")
        print(f"Expected runbooks in: {RUNBOOK_DIR}")
        return

    # Step 2: Create embeddings
    print("\n[2] Creating embeddings...")

    embeddings = create_embeddings(chunks)

    print(f"Embedding shape: {embeddings.shape}")

    # Step 3: Create FAISS index
    print("\n[3] Creating FAISS index...")

    index = create_faiss_index(embeddings)

    print(f"FAISS index contains {index.ntotal} vectors.")

    # Step 4: Test incident
    query = """
    Database connection timeout.
    Connection pool exhausted.
    Failed to execute database query.
    Payment API is experiencing increased errors
    and high request latency.
    """

    print("\n[4] Incident received:")
    print(query)

    # Step 5: Search
    print("\n[5] Searching for relevant runbooks...")

    results = search_runbooks(
        query,
        index,
        chunks,
        top_k=TOP_K
    )

    # Step 6: Display results
    print("\n" + "=" * 60)
    print("RETRIEVED RUNBOOK INFORMATION")
    print("=" * 60)

    for number, result in enumerate(results, start=1):

        print(f"\nResult {number}")
        print("-" * 60)

        print(f"Source: {result['source']}")

        print("\nContent:")
        print(result["text"])

    print("\n" + "=" * 60)
    print("RAG SEARCH COMPLETED")
    print("=" * 60)


# --------------------------------------------------
# 8. Run Program
# --------------------------------------------------

if __name__ == "__main__":
    main()