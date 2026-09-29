import re


def clean_text(text: str) -> str:
    """
    Clean extracted PDF text while preserving
    meaningful paragraph structure.
    """

    if not text:
        return ""

    # Normalize line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove excessive spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def split_into_paragraphs(text: str) -> list[str]:
    """
    Split cleaned text into paragraphs.

    Paragraphs are initially identified using
    blank lines.
    """

    if not text:
        return []

    paragraphs = re.split(r"\n\s*\n", text)

    cleaned_paragraphs = []

    for paragraph in paragraphs:

        paragraph = paragraph.strip()

        if not paragraph:
            continue

        # Join lines belonging to the same paragraph
        paragraph = re.sub(r"\s*\n\s*", " ", paragraph)

        # Remove excessive spaces
        paragraph = re.sub(r"\s+", " ", paragraph)

        paragraph = paragraph.strip()

        if paragraph:
            cleaned_paragraphs.append(paragraph)

    return cleaned_paragraphs


def process_document(pages: list[dict]) -> list[dict]:
    """
    Process the page-wise output produced by pdf_extractor.py.

    Input:
        [
            {
                "page_number": 1,
                "text": "..."
            }
        ]

    Output:
        [
            {
                "page_number": 1,
                "paragraph_number": 1,
                "text": "..."
            }
        ]
    """

    processed_document = []

    for page in pages:

        page_number = page["page_number"]
        raw_text = page["text"]

        # Clean page text
        cleaned_text = clean_text(raw_text)

        # Split page into paragraphs
        paragraphs = split_into_paragraphs(cleaned_text)

        # Store each paragraph
        for paragraph_number, paragraph in enumerate(
            paragraphs,
            start=1
        ):

            processed_document.append({
                "page_number": page_number,
                "paragraph_number": paragraph_number,
                "text": paragraph
            })

    return processed_document