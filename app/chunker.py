def chunk_text(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[str]:

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0:
        raise ValueError("overlap cannot be negative")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def chunk_pages(
    pages: list[dict],
    document_name: str,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[dict]:

    chunks = []

    for page in pages:
        page_chunks = chunk_text(
            page["text"],
            chunk_size=chunk_size,
            overlap=overlap,
        )

        for chunk in page_chunks:
            chunks.append({
                "document": document_name,
                "page": page["page"],
                "text": chunk,
            })

    return chunks