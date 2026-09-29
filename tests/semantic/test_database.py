def test_database_initialization(
    tmp_path,
):

    from app.semantic_search.database.database import (
        Database,
    )

    database_path = (
        tmp_path / "semantic_search.db"
    )

    database = Database(
        database_path
    )

    assert database_path.exists()


def test_insert_document(
    tmp_path,
):

    from app.semantic_search.database.database import (
        Database,
    )

    database = Database(
        tmp_path / "test.db"
    )

    document_id = database.insert_document(
        filename="sample.pdf",
        total_pages=10,
    )

    assert document_id > 0


def test_insert_paragraph(
    tmp_path,
):

    from app.semantic_search.database.database import (
        Database,
    )

    database = Database(
        tmp_path / "test.db"
    )

    document_id = database.insert_document(
        filename="sample.pdf",
        total_pages=1,
    )

    paragraph_id = database.insert_paragraph(
        document_id=document_id,
        page_number=1,
        paragraph_number=1,
        text=(
            "The vessel must submit "
            "documentation."
        ),
    )

    assert paragraph_id > 0