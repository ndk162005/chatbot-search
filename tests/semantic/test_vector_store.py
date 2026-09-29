def test_vector_store_initialization(
    tmp_path,
):

    from app.semantic_search.database.vector_store import (
        VectorStore,
    )

    store = VectorStore(
        persist_directory=tmp_path / "vectors"
    )

    assert store is not None


def test_add_embedding(
    tmp_path,
):

    from app.semantic_search.database.vector_store import (
        VectorStore,
    )

    store = VectorStore(
        persist_directory=tmp_path / "vectors"
    )

    store.add_documents(
        ids=["test_1"],
        embeddings=[
            [0.1, 0.2, 0.3]
        ],
        documents=[
            "Port entry requirements."
        ],
        metadatas=[
            {
                "filename": "sample.pdf",
                "page_number": 1,
            }
        ],
    )

    assert store.count() == 1


def test_vector_search(
    tmp_path,
):

    from app.semantic_search.database.vector_store import (
        VectorStore,
    )

    store = VectorStore(
        persist_directory=tmp_path / "vectors"
    )

    store.add_documents(
        ids=[
            "test_1",
            "test_2",
        ],
        embeddings=[
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
        ],
        documents=[
            "Port entry requirements.",
            "Weather conditions at sea.",
        ],
        metadatas=[
            {
                "filename": "sample.pdf",
                "page_number": 1,
            },
            {
                "filename": "sample.pdf",
                "page_number": 2,
            },
        ],
    )

    results = store.search(
        query_embedding=[
            1.0,
            0.0,
            0.0,
        ],
        top_k=1,
    )

    assert results is not None
    assert len(results["documents"]) == 1

    assert (
        results["documents"][0]
        == "Port entry requirements."
    )