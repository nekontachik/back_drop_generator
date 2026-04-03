"""Tests for ChromaDB seeding and RAG retrieval service."""

from __future__ import annotations

import pytest


class TestQueryStyles:
    """Test RAG query returns correct structure and semantic relevance."""

    def test_query_returns_list_of_dicts(self, chroma_collection):
        from app.services.rag_retriever import query_styles

        results = query_styles(chroma_collection, "dark techno warehouse", n_results=3)
        assert isinstance(results, list)
        assert len(results) == 3
        for result in results:
            assert isinstance(result, dict)

    def test_result_dict_has_required_keys(self, chroma_collection):
        from app.services.rag_retriever import query_styles

        results = query_styles(chroma_collection, "dark techno warehouse", n_results=3)
        for result in results:
            assert "id" in result
            assert "document" in result
            assert "metadata" in result
            assert "distance" in result

    def test_result_metadata_has_required_fields(self, chroma_collection):
        from app.services.rag_retriever import query_styles

        results = query_styles(chroma_collection, "dark techno warehouse", n_results=3)
        required_keys = {
            "genre",
            "colors",
            "shapes",
            "movement",
            "intensity",
            "speed",
            "effect_preference",
        }
        for result in results:
            meta = result["metadata"]
            for key in required_keys:
                assert key in meta, f"Missing metadata key: {key}"

    def test_techno_query_returns_techno_first(self, chroma_collection):
        from app.services.rag_retriever import query_styles

        results = query_styles(chroma_collection, "techno", n_results=3)
        assert results[0]["metadata"]["genre"] == "techno"

    def test_ambient_query_returns_ambient_first(self, chroma_collection):
        from app.services.rag_retriever import query_styles

        results = query_styles(
            chroma_collection, "dreamy ambient floating", n_results=3
        )
        assert results[0]["metadata"]["genre"] == "ambient"

    def test_n_results_limits_output(self, chroma_collection):
        from app.services.rag_retriever import query_styles

        results = query_styles(chroma_collection, "techno", n_results=1)
        assert len(results) == 1

    def test_intensity_and_speed_are_floats(self, chroma_collection):
        from app.services.rag_retriever import query_styles

        results = query_styles(chroma_collection, "techno", n_results=1)
        meta = results[0]["metadata"]
        assert isinstance(meta["intensity"], float)
        assert isinstance(meta["speed"], float)


class TestUpsertIdempotency:
    """Test that seeding twice does not create duplicates."""

    def test_double_seed_same_count(self, tmp_path):
        from app.services.genre_seeder import init_genre_collection

        chroma_dir = str(tmp_path / "chroma_idem")
        c1 = init_genre_collection(chroma_dir)
        count1 = c1.count()
        c2 = init_genre_collection(chroma_dir)
        count2 = c2.count()
        assert count1 == 10
        assert count2 == 10


class TestGetSetCollection:
    """Test module-level collection accessor."""

    def test_get_collection_raises_when_not_set(self):
        from app.services import rag_retriever

        # Reset module state
        rag_retriever._collection = None
        with pytest.raises(RuntimeError):
            rag_retriever.get_collection()

    def test_set_then_get_collection(self, chroma_collection):
        from app.services import rag_retriever

        rag_retriever.set_collection(chroma_collection)
        assert rag_retriever.get_collection() is chroma_collection
        # Cleanup
        rag_retriever._collection = None
