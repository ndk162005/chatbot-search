import sqlite3

from app.core.config import DATABASE_PATH


# ==================================================
# DATABASE CONNECTION
# ==================================================

def get_connection():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


# ==================================================
# INITIALIZE DATABASE
# ==================================================

def initialize_database():

    connection = get_connection()

    try:

        cursor = connection.cursor()

        # ------------------------------------------
        # DOCUMENTS TABLE
        # ------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                filename TEXT NOT NULL,

                total_pages INTEGER NOT NULL DEFAULT 0,

                uploaded_at TEXT NOT NULL

            )
        """)

        # ------------------------------------------
        # PARAGRAPHS TABLE
        # ------------------------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS paragraphs (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                document_id INTEGER NOT NULL,

                page_number INTEGER NOT NULL,

                paragraph_number INTEGER NOT NULL,

                text TEXT NOT NULL,

                FOREIGN KEY (document_id)
                    REFERENCES documents(id)
                    ON DELETE CASCADE

            )
        """)

        # ------------------------------------------
        # INDEX
        # ------------------------------------------

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_paragraph_document
            ON paragraphs(document_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_paragraph_page
            ON paragraphs(
                document_id,
                page_number
            )
        """)

        connection.commit()

    finally:

        connection.close()


# ==================================================
# INSERT DOCUMENT
# ==================================================

def insert_document(
    filename: str,
    total_pages: int,
    uploaded_at: str
) -> int:

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO documents (
                filename,
                total_pages,
                uploaded_at
            )

            VALUES (?, ?, ?)
        """, (
            filename,
            total_pages,
            uploaded_at
        ))

        connection.commit()

        return cursor.lastrowid

    finally:

        connection.close()


# ==================================================
# INSERT PARAGRAPHS
# ==================================================

def insert_paragraphs(
    document_id: int,
    paragraphs: list[dict]
):

    if not paragraphs:
        return []

    connection = get_connection()

    try:

        cursor = connection.cursor()

        inserted_ids = []

        for paragraph in paragraphs:

            cursor.execute("""
                INSERT INTO paragraphs (
                    document_id,
                    page_number,
                    paragraph_number,
                    text
                )

                VALUES (?, ?, ?, ?)
            """, (
                document_id,
                paragraph["page_number"],
                paragraph["paragraph_number"],
                paragraph["text"]
            ))

            inserted_ids.append(
                cursor.lastrowid
            )

        connection.commit()

        return inserted_ids

    finally:

        connection.close()