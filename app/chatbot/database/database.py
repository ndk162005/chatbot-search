"""
SQLite database management for the PDF chatbot.
"""

import sqlite3
from pathlib import Path
from typing import Any, Optional

from ..config import DATABASE_PATH


class Database:
    """
    Handles all SQLite operations for the chatbot.
    """

    def __init__(
        self,
        database_path: str | Path = DATABASE_PATH,
    ) -> None:

        self.database_path = Path(database_path)

        # Create parent directory if it does not exist.
        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.initialize()

    # ---------------------------------------------------------
    # Connection
    # ---------------------------------------------------------

    def get_connection(self) -> sqlite3.Connection:
        """
        Create a SQLite database connection.
        """

        connection = sqlite3.connect(
            self.database_path
        )

        connection.row_factory = sqlite3.Row

        # Enable foreign keys.
        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        return connection

    # ---------------------------------------------------------
    # Initialization
    # ---------------------------------------------------------

    def initialize(self) -> None:
        """
        Create database tables if they do not exist.
        """

        with self.get_connection() as connection:

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    total_pages INTEGER NOT NULL DEFAULT 0,
                    uploaded_at TIMESTAMP
                        DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS paragraphs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    document_id INTEGER NOT NULL,

                    page_number INTEGER NOT NULL,

                    paragraph_number INTEGER NOT NULL,

                    text TEXT NOT NULL,

                    FOREIGN KEY (
                        document_id
                    )
                    REFERENCES documents(id)
                    ON DELETE CASCADE
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_paragraph_document
                ON paragraphs(document_id)
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_paragraph_page
                ON paragraphs(
                    document_id,
                    page_number
                )
                """
            )

            connection.commit()

    # ---------------------------------------------------------
    # Documents
    # ---------------------------------------------------------

    def insert_document(
        self,
        filename: str,
        total_pages: int,
    ) -> int:
        """
        Insert a document and return its ID.
        """

        with self.get_connection() as connection:

            cursor = connection.execute(
                """
                INSERT INTO documents (
                    filename,
                    total_pages
                )
                VALUES (?, ?)
                """,
                (
                    filename,
                    total_pages,
                ),
            )

            connection.commit()

            return int(cursor.lastrowid)

    def get_document(
        self,
        document_id: int,
    ) -> Optional[dict[str, Any]]:
        """
        Retrieve a document by ID.
        """

        with self.get_connection() as connection:

            row = connection.execute(
                """
                SELECT
                    id,
                    filename,
                    total_pages,
                    uploaded_at
                FROM documents
                WHERE id = ?
                """,
                (document_id,),
            ).fetchone()

            if row is None:
                return None

            return dict(row)

    def list_documents(self) -> list[dict[str, Any]]:
        """
        Return all uploaded documents.
        """

        with self.get_connection() as connection:

            rows = connection.execute(
                """
                SELECT
                    id,
                    filename,
                    total_pages,
                    uploaded_at
                FROM documents
                ORDER BY uploaded_at DESC
                """
            ).fetchall()

            return [
                dict(row)
                for row in rows
            ]

    # ---------------------------------------------------------
    # Paragraphs
    # ---------------------------------------------------------

    def insert_paragraph(
        self,
        document_id: int,
        page_number: int,
        paragraph_number: int,
        text: str,
    ) -> int:
        """
        Insert a single paragraph.
        """

        if not text or not text.strip():
            raise ValueError(
                "Paragraph text cannot be empty."
            )

        with self.get_connection() as connection:

            cursor = connection.execute(
                """
                INSERT INTO paragraphs (
                    document_id,
                    page_number,
                    paragraph_number,
                    text
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    document_id,
                    page_number,
                    paragraph_number,
                    text.strip(),
                ),
            )

            connection.commit()

            return int(cursor.lastrowid)

    def insert_paragraphs(
        self,
        paragraphs: list[dict[str, Any]],
    ) -> list[int]:
        """
        Insert multiple paragraphs efficiently.

        Each dictionary must contain:

            document_id
            page_number
            paragraph_number
            text
        """

        if not paragraphs:
            return []

        values = []

        for paragraph in paragraphs:

            text = paragraph.get(
                "text",
                "",
            )

            if not text or not text.strip():
                continue

            values.append(
                (
                    paragraph["document_id"],
                    paragraph["page_number"],
                    paragraph["paragraph_number"],
                    text.strip(),
                )
            )

        if not values:
            return []

        with self.get_connection() as connection:

            cursor = connection.cursor()

            ids = []

            for value in values:

                cursor.execute(
                    """
                    INSERT INTO paragraphs (
                        document_id,
                        page_number,
                        paragraph_number,
                        text
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    value,
                )

                ids.append(
                    int(cursor.lastrowid)
                )

            connection.commit()

            return ids

    def get_paragraph(
        self,
        paragraph_id: int,
    ) -> Optional[dict[str, Any]]:
        """
        Retrieve a paragraph by ID.
        """

        with self.get_connection() as connection:

            row = connection.execute(
                """
                SELECT
                    p.id,
                    p.document_id,
                    p.page_number,
                    p.paragraph_number,
                    p.text,
                    d.filename
                FROM paragraphs p
                JOIN documents d
                    ON p.document_id = d.id
                WHERE p.id = ?
                """,
                (paragraph_id,),
            ).fetchone()

            if row is None:
                return None

            return dict(row)

    def get_document_paragraphs(
        self,
        document_id: int,
    ) -> list[dict[str, Any]]:
        """
        Retrieve all paragraphs belonging to a document.
        """

        with self.get_connection() as connection:

            rows = connection.execute(
                """
                SELECT
                    id,
                    document_id,
                    page_number,
                    paragraph_number,
                    text
                FROM paragraphs
                WHERE document_id = ?
                ORDER BY
                    page_number,
                    paragraph_number
                """,
                (document_id,),
            ).fetchall()

            return [
                dict(row)
                for row in rows
            ]

    # ---------------------------------------------------------
    # Delete
    # ---------------------------------------------------------

    def delete_document(
        self,
        document_id: int,
    ) -> bool:
        """
        Delete a document and its paragraphs.

        Foreign-key cascade removes the paragraphs.
        """

        with self.get_connection() as connection:

            cursor = connection.execute(
                """
                DELETE FROM documents
                WHERE id = ?
                """,
                (document_id,),
            )

            connection.commit()

            return cursor.rowcount > 0


# -------------------------------------------------------------
# Shared database instance and helper functions
# -------------------------------------------------------------

database = Database()


def create_document(filename: str, total_pages: int) -> int:
    return database.insert_document(filename=filename, total_pages=total_pages)


def insert_paragraphs(paragraphs: list[dict[str, Any]]) -> list[int]:
    return database.insert_paragraphs(paragraphs=paragraphs)