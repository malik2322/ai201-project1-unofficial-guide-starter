import json

import chromadb
from chromadb.utils import embedding_functions

from config import (
    CHROMA_COLLECTION,
    CHROMA_PATH,
    CHUNKS_FILE,
    EMBEDDING_MODEL,
    N_RESULTS,
)

_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBEDDING_MODEL
)
_client = chromadb.PersistentClient(path=CHROMA_PATH)
_collection = _client.get_or_create_collection(
    name=CHROMA_COLLECTION,
    embedding_function=_ef,
    metadata={"hnsw:space": "cosine"},
)


def get_collection():
    """Return the ChromaDB collection. Used by app.py during ingestion."""
    return _collection


def load_chunks(path=CHUNKS_FILE):
    """Load chunk records produced by ingest.py."""
    chunks = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                chunks.append(json.loads(line))
    return chunks


def embed_and_store(chunks):
    """Embed chunks and store them in the vector database."""
    _collection.add(
        documents=[c["content"] for c in chunks],
        metadatas=[
            {"source": c["source"], "parent_source": c["parent_source"]}
            for c in chunks
        ],
        ids=[c["chunk_id"] for c in chunks],
    )
    print(f"Stored {_collection.count()} total chunks in the vector database.")


def retrieve(query, n_results=N_RESULTS):
    """Find the most relevant chunks for a user's question.

    Returns a list of dicts with "text", "source", "parent_source", and
    "distance" (cosine distance — lower is more similar). Returns an empty
    list if the collection has no documents.
    """
    if _collection.count() == 0:
        return []

    results = _collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    return [
        {
            "text": text,
            "source": metadata["source"],
            "parent_source": metadata["parent_source"],
            "distance": distance,
        }
        for text, metadata, distance in zip(
            results["documents"][0], results["metadatas"][0], results["distances"][0]
        )
    ]
