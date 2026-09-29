from pdf_extractor import extract_pdf_text


def chunk_into_paragraphs(pdf_path: str) -> list[dict]:
    """
    Extract text from a PDF and split each page into paragraphs.

    A paragraph is considered to end when there is an empty line
    between two blocks of text.

    Returns:
        [
            {
                "page_number": 1,
                "paragraph_number": 1,
                "text": "First paragraph..."
            },
            {
                "page_number": 1,
                "paragraph_number": 2,
                "text": "Second paragraph..."
            }
        ]
    """

    # ---------------------------------------------------------
    # 1. Call pdf_extractor.py
    # ---------------------------------------------------------
    extracted_pages = extract_pdf_text(pdf_path)

    paragraphs = []

    # ---------------------------------------------------------
    # 2. Process every extracted page
    # ---------------------------------------------------------
    for page in extracted_pages:

        page_number = page["page_number"]
        page_text = page["text"]

        # -----------------------------------------------------
        # 3. Split whenever there is a completely empty line
        #
        # Example:
        #
        # Paragraph one.
        #
        # Paragraph two.
        #
        # becomes:
        #
        # ["Paragraph one.", "Paragraph two."]
        # -----------------------------------------------------

        page_paragraphs = page_text.split("\n\n")

        paragraph_number = 1

        # -----------------------------------------------------
        # 4. Clean and store each paragraph
        # -----------------------------------------------------
        for paragraph in page_paragraphs:

            # Remove leading/trailing whitespace
            paragraph = paragraph.strip()

            # Ignore empty paragraphs
            if not paragraph:
                continue

            paragraphs.append({
                "page_number": page_number,
                "paragraph_number": paragraph_number,
                "text": paragraph
            })

            paragraph_number += 1

    return paragraphs


# =============================================================
# TEST THE PARAGRAPH CHUNKER
# =============================================================

if __name__ == "__main__":

    pdf_file = r"data/pdfs/sample.pdf"

    chunks = chunk_into_paragraphs(pdf_file)

    print(f"\nTotal paragraphs extracted: {len(chunks)}\n")

    for chunk in chunks:

        print("=" * 80)
        print(
            f"Page: {chunk['page_number']} | "
            f"Paragraph: {chunk['paragraph_number']}"
        )
        print("=" * 80)

        print(chunk["text"])
        print()