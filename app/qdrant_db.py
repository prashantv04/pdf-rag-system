import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

# Load variables from .env
load_dotenv()

# Safely get variables, defaulting to localhost if not found
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

COLLECTION_NAME = "documents"
VECTOR_SIZE = 384


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        timeout=60,
    )


def reset_collection(client: QdrantClient) -> None:
    collections = client.get_collections()

    existing_collections = {
        collection.name
        for collection in collections.collections
    }

    if COLLECTION_NAME in existing_collections:
        print(f"Deleting existing Qdrant collection: {COLLECTION_NAME}")

        client.delete_collection(
            collection_name=COLLECTION_NAME
        )

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE,
        ),
    )

    print(f"Created fresh Qdrant collection: {COLLECTION_NAME}")


def create_collection(client: QdrantClient) -> None:
    collections = client.get_collections()

    existing_collections = {
        collection.name
        for collection in collections.collections
    }

    if COLLECTION_NAME not in existing_collections:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )

        print(f"Created Qdrant collection: {COLLECTION_NAME}")
    else:
        print(f"Qdrant collection already exists: {COLLECTION_NAME}")


def insert_chunks(
    client: QdrantClient,
    chunks: list[dict],
    embeddings: list[list[float]],
    batch_size: int = 250,
) -> None:

    if len(chunks) != len(embeddings):
        raise ValueError(
            "The number of chunks must match the number of embeddings."
        )

    total = len(chunks)
    points = []

    for index, (chunk, embedding) in enumerate(
        zip(chunks, embeddings),
        start=1,
    ):
        points.append(
            PointStruct(
                id=index,
                vector=embedding,
                payload={
                    "document": chunk["document"],
                    "page": chunk["page"],
                    "text": chunk["text"],
                },
            )
        )

    print(f"Uploading {total} chunks to Qdrant in batches of {batch_size}...")

    # Upload in manageable chunks
    for i in range(0, total, batch_size):
        batch = points[i : i + batch_size]
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=batch,
        )
        print(f"Uploaded {min(i + batch_size, total)} / {total} chunks...")

    print(f"Successfully inserted all {total} chunks into Qdrant.")


def search(
    client: QdrantClient,
    query_embedding: list[float],
    limit: int = 5,
    score_threshold: float | None = None,
) -> list:

    # Retrieve extra results so we can remove duplicate pages.
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=limit * 3,
        score_threshold=score_threshold,
    ).points

    unique_results = []
    seen_pages = set()

    for result in results:
        document = result.payload["document"]
        page = result.payload["page"]

        page_key = (document, page)

        if page_key in seen_pages:
            continue

        seen_pages.add(page_key)
        unique_results.append(result)

        if len(unique_results) >= limit:
            break

    return unique_results