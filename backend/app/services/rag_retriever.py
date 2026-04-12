"""RAG query service for genre-style document retrieval.

Provides semantic search over ChromaDB genre-style collection,
returning ranked results with metadata for the LLM blender.
"""

from __future__ import annotations

import chromadb

# Module-level collection reference, set during app startup.
_collection: chromadb.Collection | None = None


def get_collection() -> chromadb.Collection:
    """Return the active ChromaDB genre-styles collection.

    Raises:
        RuntimeError: If the collection has not been initialized via
            :func:`set_collection`.
    """
    if _collection is None:
        raise RuntimeError(
            "ChromaDB collection not initialized. "
            "Call set_collection() during app startup."
        )
    return _collection


def set_collection(collection: chromadb.Collection) -> None:
    """Set the module-level ChromaDB collection reference.

    Args:
        collection: A seeded ChromaDB collection.
    """
    global _collection
    _collection = collection


def query_styles(
    collection: chromadb.Collection,
    prompt: str,
    n_results: int = 3,
) -> list[dict]:
    """Query genre-style documents by text prompt.

    Args:
        collection: ChromaDB collection to query.
        prompt: User's text prompt describing desired visual style.
        n_results: Maximum number of results to return.

    Returns:
        List of flat dicts matching the frontend StyleMatch interface, each
        with keys: ``id``, ``genre``, ``description``, ``colors``, ``shapes``,
        ``movement``, ``intensity``, ``speed``, ``effect_preference``,
        ``distance``.  Sorted by ascending distance (most relevant first).

        - ``colors`` and ``shapes`` are lists of strings (split from
          comma-joined ChromaDB metadata).
        - ``intensity`` and ``speed`` are floats.
    """
    results = collection.query(
        query_texts=[prompt],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    styles: list[dict] = []
    for i in range(len(results["ids"][0])):
        metadata = results["metadatas"][0][i]
        colors_raw = metadata.get("colors", "")
        shapes_raw = metadata.get("shapes", "")

        styles.append(
            {
                "id": results["ids"][0][i],
                "description": results["documents"][0][i],
                "genre": metadata.get("genre", "unknown"),
                "colors": [c.strip() for c in colors_raw.split(",") if c.strip()] if colors_raw else [],
                "shapes": [s.strip() for s in shapes_raw.split(",") if s.strip()] if shapes_raw else [],
                "movement": metadata.get("movement", ""),
                "intensity": float(metadata.get("intensity", 0.5)),
                "speed": float(metadata.get("speed", 0.5)),
                "effect_preference": metadata.get("effect_preference", ""),
                "distance": results["distances"][0][i],
            }
        )

    return styles
