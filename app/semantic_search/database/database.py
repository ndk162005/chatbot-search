"""
Database management for semantic search.
"""

import sqlite3
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
from ..core.config import DATABASE_PATH
from .models import Document, Paragraph


class Database:
    """
    Database class interface for semantic search.
    """

    def __init__(self, database_path: str | Path = DATABASE_PATH) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.database_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def initialize(self) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL DEFAULT '',
                file_size INTEGER NOT NULL DEFAULT 0,
                total_pages INTEGER NOT NULL DEFAULT 0,
                total_paragraphs INTEGER NOT NULL DEFAULT 0,
                created_at REAL NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS paragraphs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER NOT NULL,
                page_number INTEGER NOT NULL DEFAULT 1,
                paragraph_number INTEGER NOT NULL DEFAULT 1,
                text TEXT NOT NULL,
                vector_id TEXT,
                FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE
            )
        """)
        conn.commit()
        conn.close()

    def insert_document(
        self,
        filename: str,
        total_pages: int = 1,
        filepath: str = "",
        file_size: int = 0,
        total_paragraphs: int = 0,
    ) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        created_at = time.time()
        cursor.execute("""
            INSERT INTO documents (filename, filepath, file_size, total_pages, total_paragraphs, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (filename, filepath, file_size, total_pages, total_paragraphs, created_at))
        doc_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return doc_id

    def insert_paragraph(
        self,
        document_id: int,
        page_number: int,
        paragraph_number: int,
        text: str,
        vector_id: str | None = None,
    ) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        if vector_id is None:
            vector_id = f"doc_{document_id}_p{page_number}_para{paragraph_number}"

        cursor.execute("""
            INSERT INTO paragraphs (document_id, page_number, paragraph_number, text, vector_id)
            VALUES (?, ?, ?, ?, ?)
        """, (document_id, page_number, paragraph_number, text, vector_id))

        para_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return para_id


def get_db_connection() -> sqlite3.Connection:
    return Database().get_connection()


def initialize_database():
    Database().initialize()


def add_document(filename: str, filepath: str, file_size: int, total_pages: int, total_paragraphs: int) -> int:
    return Database().insert_document(
        filename=filename,
        filepath=filepath,
        file_size=file_size,
        total_pages=total_pages,
        total_paragraphs=total_paragraphs,
    )


def add_paragraphs(document_id: int, paragraphs_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    db = Database()
    records = []
    for item in paragraphs_data:
        page_num = item.get("page_number", 1)
        para_num = item.get("paragraph_number", 1)
        text = item.get("text", "")
        vector_id = item.get("id") or f"doc_{document_id}_p{page_num}_para{para_num}"
        db_id = db.insert_paragraph(document_id, page_num, para_num, text, vector_id)
        records.append({
            "id": vector_id,
            "db_id": db_id,
            "document_id": document_id,
            "page_number": page_num,
            "paragraph_number": para_num,
            "text": text
        })
    return records


def get_all_documents() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_document_by_id(doc_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def delete_document(doc_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM paragraphs WHERE document_id = ?", (doc_id,))
    cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted
