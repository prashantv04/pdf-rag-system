from pathlib import Path

import fitz


def read_pdf(file_path: str | Path) -> list[dict]:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a PDF file: {path}")

    document = fitz.open(path)

    pages = []

    for page_number, page in enumerate(document, start=1):
        text = page.get_text("text").strip()

        if text:
            pages.append({
                "page": page_number,
                "text": text,
            })

    document.close()

    return pages