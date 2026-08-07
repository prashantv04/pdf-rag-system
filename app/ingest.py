from pathlib import Path

from app.chunker import chunk_pages
from app.embeddings import EmbeddingModel
from app.pdf_reader import read_pdf
from app.qdrant_db import (
    reset_collection,
    get_qdrant_client,
    insert_chunks,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def main():
    pdf_files = sorted(DATA_DIR.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in: {DATA_DIR}")
        return

    all_chunks = []

    for pdf_path in pdf_files:
        print(f"\nReading PDF: {pdf_path.name}")

        pages = read_pdf(pdf_path)

        print(f"Total pages: {len(pages)}")

        chunks = chunk_pages(
            pages,
            document_name=pdf_path.name,
        )

        print(f"Chunks from {pdf_path.name}: {len(chunks)}")

        all_chunks.extend(chunks)

    print(f"\nTotal chunks: {len(all_chunks)}")

    if not all_chunks:
        print("No chunks were created.")
        return

    print("\nLoading embedding model...")

    embedding_model = EmbeddingModel()

    texts = [chunk["text"] for chunk in all_chunks]

    print(f"Embedding {len(texts)} chunks...")

    embeddings = embedding_model.encode(texts)

    print(f"Embedding count: {len(embeddings)}")
    print(f"Embedding dimensions: {len(embeddings[0])}")

    qdrant = get_qdrant_client()

    reset_collection(qdrant)

    insert_chunks(
        client=qdrant,
        chunks=all_chunks,
        embeddings=embeddings,
    )

    print("\nIngestion completed successfully.")


if __name__ == "__main__":
    main()