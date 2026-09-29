def test_database_initialization(
    tmp_path,
):
    """
    Verify that the chatbot database
    initializes correctly.
    """

    from app.chatbot.database.database import (
        Database,
    )

    database_path = (
        tmp_path / "test_chatbot.db"
    )

    database = Database(
        database_path
    )

    assert database_path.exists()


def test_insert_document(
    tmp_path,
):
    """
    Verify document insertion.
    """

    from app.chatbot.database.database import (
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

    document = database.get_document(
        document_id
    )

    assert document is not None
    assert document["filename"] == "sample.pdf"
    assert document["total_pages"] == 10


def test_insert_paragraph(
    tmp_path,
):
    """
    Verify paragraph insertion.
    """

    from app.chatbot.database.database import (
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
        text="This is a test paragraph.",
    )

    assert paragraph_id > 0

    paragraph = database.get_paragraph(
        paragraph_id
    )

    assert paragraph is not None

    assert (
        paragraph["text"]
        == "This is a test paragraph."
    )