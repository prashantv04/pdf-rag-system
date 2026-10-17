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

    # 1. State Machine Start: Default to Majority opinion
    current_opinion = "Majority"

    for page in pages:
        page_chunks = chunk_text(
            page["text"],
            chunk_size=chunk_size,
            overlap=overlap,
        )

        for chunk in page_chunks:
            # 2. Check the text to see if the opinion changed
            text_lower = chunk.lower()
            if "dissenting" in text_lower:
                current_opinion = "Dissenting"
            elif "concurring" in text_lower:
                current_opinion = "Concurring"
            elif "majority opinion" in text_lower:
                current_opinion = "Majority"

            # 3. Append the chunk with the new metadata tag
            chunks.append({
                "document": document_name,
                "page": page["page"],
                "text": chunk,
                "opinion_type": current_opinion,  # NEW: The sticky note!
            })

    return chunks