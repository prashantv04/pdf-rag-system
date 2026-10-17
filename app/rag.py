def build_context(results: list) -> str:
    context_parts = []

    for index, result in enumerate(results, start=1):
        document = result.payload.get("document", "Unknown")
        page = result.payload.get("page", "Unknown")
        # Grab the new metadata (default to Majority if missing)
        opinion = result.payload.get("opinion_type", "Majority")
        text = result.payload.get("text", "").strip()

        context_parts.append(
            f"Source {index} ({opinion} Opinion) Document: {document} Page: {page} Retrieved Text: {text}"
        )

    return "\n\n".join(context_parts)


def build_citations(results: list) -> str:
    citation_parts = []

    for index, result in enumerate(results, start=1):
        document = result.payload.get("document", "Unknown")
        page = result.payload.get("page", "Unknown")
        # Grab the new metadata for the UI
        opinion = result.payload.get("opinion_type", "Majority")
        text = result.payload.get("text", "").strip()

        # Clean up whitespace
        snippet = " ".join(text.split())

        # Smart Truncation: Stop at 400 chars, but don't cut words in half
        if len(snippet) > 400:
            truncated = snippet[:400]
            last_space_index = truncated.rfind(" ")

            if last_space_index != -1:
                snippet = truncated[:last_space_index] + "..."
            else:
                snippet = truncated + "..."

        citation_parts.append(
            f"**Source {index} ({opinion} Opinion)**\n"
            f"Document: {document}\n"
            f"Page: {page}\n"
            f"Snippet: {snippet}"
        )

    return "\n\n".join(citation_parts)


def deduplicate_results(results: list) -> list:
    """
    Keep only the highest-scoring result for each document/page.
    """
    seen = set()
    unique_results = []

    for result in results:
        document = result.payload.get("document", "Unknown")
        page = result.payload.get("page", "Unknown")

        key = (document, page)

        if key in seen:
            continue

        seen.add(key)
        unique_results.append(result)

    return unique_results