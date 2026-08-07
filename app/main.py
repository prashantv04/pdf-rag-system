from pathlib import Path

from app.embeddings import EmbeddingModel
from app.llm import generate_answer
from app.rag import build_context, build_citations, deduplicate_results
from app.qdrant_db import get_qdrant_client, search


PROJECT_ROOT = Path(__file__).resolve().parent.parent

RELEVANCE_THRESHOLD = 0.20
RETRIEVAL_LIMIT = 5


def main():
    print("Loading embedding model...")

    embedding_model = EmbeddingModel()

    qdrant = get_qdrant_client()

    print("Connected to Qdrant.")

    query = input("\nAsk a question: ").strip()

    if not query:
        print("Please enter a question.")
        return

    print("\nSearching documents...")

    query_embedding = embedding_model.encode([query])[0]

    results = search(
        client=qdrant,
        query_embedding=query_embedding,
        limit=RETRIEVAL_LIMIT,
        score_threshold=RELEVANCE_THRESHOLD,
    )

    results = deduplicate_results(results)

    if not results:
        print("\n--- Answer ---")
        print("The information is not available in the supplied documents.")
        return

    # print(f"Retrieved results: {len(results)}")
    print(f"Retrieved {len(results)} relevant sources.")

    for index, result in enumerate(results, start=1):
        print(
            f"Retrieved {index}: "
            f"{result.payload['document']} "
            f"page {result.payload['page']} "
            f"(score={result.score:.3f})"
        )

    context = build_context(results)

    print("\nGenerating answer...")

    answer = generate_answer(
        question=query,
        context=context,
    )

    citations = build_citations(results)

    print("\n--- Answer ---")
    print(answer)

    print("\n--- Sources ---")
    print(citations)


if __name__ == "__main__":
    main()
