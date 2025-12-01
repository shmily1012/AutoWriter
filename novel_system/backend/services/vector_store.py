import logging
from array import array
from typing import Dict, List, Optional

import redis
from redis.commands.search.field import NumericField, TagField, TextField, VectorField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.commands.search.query import Query

from novel_system.backend.core.config import get_settings
from novel_system.backend.services.openai_client import embed_texts

logger = logging.getLogger(__name__)

settings = get_settings()
INDEX_NAME = "idx_novel_chunks"
DOC_PREFIX = "chunk:"
VECTOR_FIELD = "embedding"


def get_redis() -> redis.Redis:
    return redis.Redis.from_url(settings.redis_url)


def ensure_index(dim: int) -> None:
    """Create RediSearch HNSW index if it does not exist."""
    r = get_redis()
    try:
        info = r.ft(INDEX_NAME).info()
        # Index exists; nothing to do.
        return
    except Exception:
        pass

    schema = (
        NumericField("project_id", sortable=True),
        TagField("type"),
        TagField("ref_id"),
        TextField("content"),
        VectorField(
            VECTOR_FIELD,
            "HNSW",
            {
                "TYPE": "FLOAT32",
                "DIM": dim,
                "DISTANCE_METRIC": "COSINE",
                "M": 40,
                "EF_CONSTRUCTION": 200,
            },
        ),
    )
    definition = IndexDefinition(prefix=[DOC_PREFIX], index_type=IndexType.HASH)
    r.ft(INDEX_NAME).create_index(schema, definition=definition)
    logger.info("Created RediSearch index %s", INDEX_NAME)


def _to_bytes(vec: List[float]) -> bytes:
    return array("f", vec).tobytes()


def chunk_text(text: str, chunk_size: int = 600, overlap: int = 100) -> List[str]:
    """Simple char-based chunking with overlap."""
    if not text:
        return []
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunks.append(text[start:end])
        if end == text_len:
            break
        start = end - overlap
    return chunks


def delete_chunks(project_id: int, ref_type: str, ref_id: int) -> None:
    r = get_redis()
    pattern = f"{DOC_PREFIX}{project_id}:{ref_type}:{ref_id}:*"
    keys = list(r.scan_iter(pattern))
    if keys:
        r.delete(*keys)


def upsert_embedding(project_id: int, ref_type: str, ref_id: int, content: str) -> None:
    """Chunk content, embed each chunk, and store in Redis vector index."""
    if not content:
        delete_chunks(project_id, ref_type, ref_id)
        return

    chunks = chunk_text(content)
    if not chunks:
        delete_chunks(project_id, ref_type, ref_id)
        return

    embeddings = embed_texts(chunks)
    dim = len(embeddings[0])
    ensure_index(dim)

    r = get_redis()
    pipe = r.pipeline()
    delete_chunks(project_id, ref_type, ref_id)
    for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        doc_id = f"{DOC_PREFIX}{project_id}:{ref_type}:{ref_id}:{idx}"
        pipe.hset(
            doc_id,
            mapping={
                "project_id": project_id,
                "type": ref_type,
                "ref_id": ref_id,
                "content": chunk,
                VECTOR_FIELD: _to_bytes(embedding),
            },
        )
    pipe.execute()


def query_similar(project_id: int, query: str, top_k: int = 5) -> List[Dict]:
    """Search similar chunks for a project."""
    if not query:
        return []
    # Ensure index exists by embedding query and checking dimension.
    query_vec = embed_texts([query])[0]
    dim = len(query_vec)
    ensure_index(dim)

    r = get_redis()
    q = (
        Query(f"@project_id:[{project_id} {project_id}]=>[KNN {top_k} @{VECTOR_FIELD} $vec]")
        .return_fields("content", "type", "ref_id", "project_id", "score")
        .dialect(2)
    )
    params = {"vec": _to_bytes(query_vec)}
    res = r.ft(INDEX_NAME).search(q, query_params=params)
    results = []
    for doc in res.docs:
        results.append(
            {
                "content": getattr(doc, "content", ""),
                "type": getattr(doc, "type", ""),
                "ref_id": int(getattr(doc, "ref_id", 0)),
                "project_id": int(getattr(doc, "project_id", 0)),
                "score": getattr(doc, "score", None),
            }
        )
    return results


def search_related_text(project_id: int, query: str, top_k: int = 5) -> List[Dict]:
    return query_similar(project_id=project_id, query=query, top_k=top_k)


__all__ = [
    "upsert_embedding",
    "query_similar",
    "search_related_text",
    "chunk_text",
]
