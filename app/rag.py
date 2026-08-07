def build_context(results: list) -> str:
    context_parts = []

    for index, result in enumerate(results, start=1):
        document = result.payload["document"]
        page = result.payload["page"]
        text = result.payload["text"].strip()

        context_parts.append(
            f"""Source {index} Document: {document} Page: {page} Retrieved Text: {text}"""
        )

    return "\n\n".join(context_parts)


def build_citations(results: list) -> str:
    citation_parts = []

    for index, result in enumerate(results, start=1):
        document = result.payload["document"]
        page = result.payload["page"]
        text = result.payload["text"].strip()

        # Keep the citation readable.
        snippet = " ".join(text.split())

        if len(snippet) > 400:
            snippet = snippet[:400] + "..."

        citation_parts.append(
            f"Source {index}\n"
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
        document = result.payload["document"]
        page = result.payload["page"]

        key = (document, page)

        if key in seen:
            continue

        seen.add(key)
        unique_results.append(result)

    return unique_results