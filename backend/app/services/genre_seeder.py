"""ChromaDB collection initialization and genre document seeding.

Loads genre-style YAML documents from data/genres/ and upserts them
into a persistent ChromaDB collection for RAG retrieval.
"""

from __future__ import annotations

from pathlib import Path

import chromadb
import yaml


def init_genre_collection(
    persist_dir: str = "data/chroma",
    genres_dir: str | Path | None = None,
) -> chromadb.Collection:
    """Initialize ChromaDB and seed genre-style documents from YAML files.

    Args:
        persist_dir: Path to ChromaDB persistent storage directory.
        genres_dir: Path to directory containing genre YAML files.
            Defaults to ``data/genres`` relative to the backend root.

    Returns:
        The seeded ChromaDB collection.
    """
    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_or_create_collection(
        name="genre_styles",
        metadata={"hnsw:space": "cosine"},
    )

    if genres_dir is None:
        genres_dir = Path(__file__).resolve().parent.parent.parent / "data" / "genres"
    else:
        genres_dir = Path(genres_dir)

    if not genres_dir.exists():
        return collection

    docs: list[str] = []
    ids: list[str] = []
    metadatas: list[dict] = []

    for yaml_file in sorted(genres_dir.glob("*.yaml")):
        genre_data = yaml.safe_load(yaml_file.read_text())
        if genre_data is None:
            continue

        docs.append(genre_data["description"].strip())
        ids.append(genre_data["id"])
        metadatas.append(
            {
                "genre": genre_data["genre"],
                "subgenre": genre_data.get("subgenre", ""),
                "colors": ",".join(genre_data.get("colors", [])),
                "shapes": ",".join(genre_data.get("shapes", [])),
                "movement": genre_data.get("movement", ""),
                "intensity": float(genre_data.get("intensity", 0.5)),
                "speed": float(genre_data.get("speed", 0.5)),
                "effect_preference": genre_data.get("effect_preference", "tunnel"),
            }
        )

    if docs:
        collection.upsert(documents=docs, ids=ids, metadatas=metadatas)

    return collection
