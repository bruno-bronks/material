from functools import lru_cache

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from app.config import get_settings

COLLECTIONS = ("papers", "materials", "summaries")


@lru_cache
def get_client():
    settings = get_settings()
    return chromadb.PersistentClient(path=settings.chroma_persist_dir)


@lru_cache
def get_embedding_function():
    settings = get_settings()
    return SentenceTransformerEmbeddingFunction(model_name=settings.embedding_model)


@lru_cache
def get_collection(name: str):
    if name not in COLLECTIONS:
        raise ValueError(f"Coleção desconhecida: {name}")
    return get_client().get_or_create_collection(
        name=name, embedding_function=get_embedding_function()
    )


def add_documents(
    collection_name: str, ids: list[str], documents: list[str], metadatas: list[dict]
) -> None:
    if not documents:
        return
    get_collection(collection_name).upsert(ids=ids, documents=documents, metadatas=metadatas)


def query(collection_name: str, query_text: str, n_results: int = 4) -> list[dict]:
    collection = get_collection(collection_name)
    count = collection.count()
    if count == 0:
        return []

    result = collection.query(query_texts=[query_text], n_results=min(n_results, count))

    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    return [
        {"document": doc, "metadata": meta, "distance": dist}
        for doc, meta, dist in zip(documents, metadatas, distances)
    ]
