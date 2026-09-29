"""
Document processor for the chatbot.

Takes extracted PDF pages and converts them into clean,
searchable text chunks while preserving document metadata.
"""

from __future__ import annotations

import re
from typing import Any


class DocumentProcessor:
    """
    Processes extracted PDF pages into searchable text chunks.

    Expected input format:

        [
            {
                "page_number": 1,
                "text": "Some text from page 1..."
            },
            {
                "page_number": 2,
                "text": "Some text from page 2..."
            }
        ]

    Output format:

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

    def __init__(
        self,
        max_chunk_size: int = 1200,
        chunk_overlap: int = 150,
        min_chunk_size: int = 30,
    ) -> None:
        """
        Initialize the document processor.

        Args:
            max_chunk_size:
                Maximum approximate number of characters in a chunk.

            chunk_overlap:
                Number of characters to overlap when a paragraph
                must be split into multiple chunks.

            min_chunk_size:
                Ignore chunks smaller than this value.
        """

        if max_chunk_size <= 0:
            raise ValueError("max_chunk_size must be greater than 0.")

        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative.")

        if chunk_overlap >= max_chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than max_chunk_size."
            )

        if min_chunk_size < 0:
            raise ValueError("min_chunk_size cannot be negative.")

        self.max_chunk_size = max_chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size

    # ---------------------------------------------------------
    # PUBLIC METHOD
    # ---------------------------------------------------------

    def process_document(
        self,
        pages: list[dict[str, Any]],
        document_id: int | None = None,
        filename: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Process all extracted PDF pages.

        Args:
            pages:
                List of extracted PDF pages.

            document_id:
                Database ID of the document.

            filename:
                Original PDF filename.

        Returns:
            List of processed chunks.
        """

        if not pages:
            return []

        processed_chunks: list[dict[str, Any]] = []

        global_chunk_number = 1

        for page in pages:

            page_number = page.get("page_number")
            page_text = page.get("text", "")

            if page_number is None:
                continue

            if not isinstance(page_text, str):
                continue

            page_text = self.clean_text(page_text)

            if not page_text:
                continue

            paragraphs = self.split_into_paragraphs(page_text)

            paragraph_number = 1

            for paragraph in paragraphs:

                paragraph = self.clean_text(paragraph)

                if not paragraph:
                    continue

                chunks = self.chunk_text(paragraph)

                for chunk in chunks:

                    chunk = self.clean_text(chunk)

                    if len(chunk) < self.min_chunk_size:
                        continue

                    processed_chunks.append(
                        {
                            "document_id": document_id,
                            "filename": filename,
                            "page_number": page_number,
                            "paragraph_number": paragraph_number,
                            "chunk_number": global_chunk_number,
                            "text": chunk,
                        }
                    )

                    global_chunk_number += 1

                paragraph_number += 1

        return processed_chunks

    # ---------------------------------------------------------
    # TEXT CLEANING
    # ---------------------------------------------------------

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean extracted PDF text.

        Removes:
        - excessive spaces
        - excessive newlines
        - leading/trailing whitespace
        """

        if not text:
            return ""

        # Normalize line endings.
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        # Remove spaces before/after newlines.
        text = re.sub(r"[ \t]+\n", "\n", text)
        text = re.sub(r"\n[ \t]+", "\n", text)

        # Replace multiple spaces/tabs with one space.
        text = re.sub(r"[ \t]+", " ", text)

        # Reduce excessive blank lines.
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    # ---------------------------------------------------------
    # PARAGRAPH DETECTION
    # ---------------------------------------------------------

    @staticmethod
    def split_into_paragraphs(text: str) -> list[str]:
        """
        Split page text into paragraphs.

        Primarily uses blank lines as paragraph boundaries.

        If the PDF extractor produces text without blank lines,
        sentence-based fallback processing is used.
        """

        if not text:
            return []

        # First attempt: split using blank lines.
        paragraphs = re.split(r"\n\s*\n", text)

        paragraphs = [
            paragraph.strip()
            for paragraph in paragraphs
            if paragraph.strip()
        ]

        if len(paragraphs) > 1:
            return paragraphs

        # If there are no obvious paragraph boundaries,
        # treat individual lines as potential paragraphs.
        lines = [
            line.strip()
            for line in text.split("\n")
            if line.strip()
        ]

        if len(lines) > 1:
            paragraphs = DocumentProcessor._combine_lines(lines)

            if paragraphs:
                return paragraphs

        return [text.strip()]

    @staticmethod
    def _combine_lines(lines: list[str]) -> list[str]:
        """
        Combine PDF lines into more meaningful paragraphs.

        PDF extraction often places every visual line on a separate
        line even though those lines belong to the same paragraph.
        """

        if not lines:
            return []

        paragraphs: list[str] = []
        current = ""

        for line in lines:

            # Detect likely headings.
            is_heading = (
                len(line) < 100
                and (
                    line.isupper()
                    or re.match(r"^\d+(\.\d+)*\.?\s+", line)
                    or re.match(r"^[A-Z][A-Za-z\s]{2,60}:$", line)
                )
            )

            if is_heading:

                if current:
                    paragraphs.append(current.strip())
                    current = ""

                paragraphs.append(line)
                continue

            if not current:
                current = line
                continue

            # If the previous line appears incomplete,
            # continue the same paragraph.
            if not re.search(r"[.!?:;]$", current):

                current += " " + line

            else:

                # A new sentence may still belong to the same paragraph.
                current += " " + line

        if current:
            paragraphs.append(current.strip())

        return paragraphs

    # ---------------------------------------------------------
    # CHUNKING
    # ---------------------------------------------------------

    def chunk_text(self, text: str) -> list[str]:
        """
        Split large paragraphs into smaller overlapping chunks.

        Short paragraphs remain unchanged.

        Large paragraphs are split approximately according to
        max_chunk_size.
        """

        text = self.clean_text(text)

        if not text:
            return []

        if len(text) <= self.max_chunk_size:
            return [text]

        chunks: list[str] = []

        start = 0
        text_length = len(text)

        while start < text_length:

            end = min(
                start + self.max_chunk_size,
                text_length,
            )

            # Try to find a natural breaking point.
            if end < text_length:

                break_position = self._find_break_position(
                    text,
                    start,
                    end,
                )

                if break_position > start:
                    end = break_position

            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end >= text_length:
                break

            next_start = end - self.chunk_overlap

            # Prevent infinite loops.
            if next_start <= start:
                next_start = end

            start = next_start

        return chunks

    # ---------------------------------------------------------
    # NATURAL BREAK DETECTION
    # ---------------------------------------------------------

    @staticmethod
    def _find_break_position(
        text: str,
        start: int,
        end: int,
    ) -> int:
        """
        Find a natural position at which to split a large chunk.

        Priority:

        1. Paragraph/newline
        2. Sentence ending
        3. Comma/semicolon
        4. Space
        """

        search_start = start + 100

        if search_start >= end:
            search_start = start

        # Prefer newline.
        newline_position = text.rfind(
            "\n",
            search_start,
            end,
        )

        if newline_position > start:
            return newline_position

        # Prefer sentence boundaries.
        sentence_matches = list(
            re.finditer(
                r"[.!?](?=\s|$)",
                text[start:end],
            )
        )

        if sentence_matches:

            match = sentence_matches[-1]

            position = start + match.end()

            if position > start:
                return position

        # Try semicolon or colon.
        punctuation_positions = [
            text.rfind(";", search_start, end),
            text.rfind(":", search_start, end),
            text.rfind(",", search_start, end),
        ]

        valid_positions = [
            position
            for position in punctuation_positions
            if position > start
        ]

        if valid_positions:
            return max(valid_positions) + 1

        # Finally split at a space.
        space_position = text.rfind(
            " ",
            search_start,
            end,
        )

        if space_position > start:
            return space_position

        return end


# -------------------------------------------------------------
# CONVENIENCE FUNCTION
# -------------------------------------------------------------

def process_document(
    pages: list[dict[str, Any]],
    document_id: int | None = None,
    filename: str | None = None,
    max_chunk_size: int = 1200,
    chunk_overlap: int = 150,
    min_chunk_size: int = 30,
) -> list[dict[str, Any]]:
    """
    Convenience function for processing a PDF document.
    """

    processor = DocumentProcessor(
        max_chunk_size=max_chunk_size,
        chunk_overlap=chunk_overlap,
        min_chunk_size=min_chunk_size,
    )

    return processor.process_document(
        pages=pages,
        document_id=document_id,
        filename=filename,
    )