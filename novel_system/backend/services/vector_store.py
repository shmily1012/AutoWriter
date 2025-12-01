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


class VectorStore:
    INDEX_NAME = "idx_novel_chunks"
    DOC_PREFIX = "chunk:"
    VECTOR_FIELD = "embedding"

    def __init__(self, redis_url: str):
        self.redis_url = redis_url

    def client(self) -> redis.Redis:
        return redis.Redis.from_url(self.redis_url)

    def ensure_index(self, dim: int) -> None:
        r = self.client()
        try:
            r.ft(self.INDEX_NAME).info()
            return
        except Exception:
            pass

        schema = (
            NumericField("project_id", sortable=True),
            TagField("type"),
            TagField("ref_id"),
            TextField("content"),
            VectorField(
                self.VECTOR_FIELD,
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
        definition = IndexDefinition(prefix=[self.DOC_PREFIX], index_type=IndexType.HASH)
        r.ft(self.INDEX_NAME).create_index(schema, definition=definition)
        logger.info("Created RediSearch index %s", self.INDEX_NAME)

    @staticmethod
    def _to_bytes(vec: List[float]) -> bytes:
        return array("f", vec).tobytes()

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 600, overlap: int = 100) -> List[str]:
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

    def delete_chunks(self, project_id: int, ref_type: str, ref_id: int) -> None:
        r = self.client()
        pattern = f"{self.DOC_PREFIX}{project_id}:{ref_type}:{ref_id}:*"
        keys = list(r.scan_iter(pattern))
        if keys:
            r.delete(*keys)

    def upsert_embedding(self, project_id: int, ref_type: str, ref_id: int, content: str) -> None:
        if not content:
            self.delete_chunks(project_id, ref_type, ref_id)
            return
        chunks = self.chunk_text(content)
        if not chunks:
            self.delete_chunks(project_id, ref_type, ref_id)
            return
        embeddings = embed_texts(chunks)
        dim = len(embeddings[0])
        self.ensure_index(dim)
        r = self.client()
        pipe = r.pipeline()
        self.delete_chunks(project_id, ref_type, ref_id)
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            doc_id = f"{self.DOC_PREFIX}{project_id}:{ref_type}:{ref_id}:{idx}"
            pipe.hset(
                doc_id,
                mapping={
                    "project_id": project_id,
                    "type": ref_type,
                    "ref_id": ref_id,
                    "content": chunk,
                    self.VECTOR_FIELD: self._to_bytes(embedding),
                },
            )
        pipe.execute()

    def query_similar(self, project_id: int, query: str, top_k: int = 5) -> List[Dict]:
        if not query:
            return []
        query_vec = embed_texts([query])[0]
        dim = len(query_vec)
        self.ensure_index(dim)
        r = self.client()
        q = (
            Query(f"@project_id:[{project_id} {project_id}]=>[KNN {top_k} @{self.VECTOR_FIELD} $vec]")
            .return_fields("content", "type", "ref_id", "project_id", "score")
            .dialect(2)
        )
        params = {"vec": self._to_bytes(query_vec)}
        res = r.ft(self.INDEX_NAME).search(q, query_params=params)
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


_store: Optional[VectorStore] = None


def get_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore(redis_url=settings.redis_url)
    return _store


def chunk_text(text: str, chunk_size: int = 600, overlap: int = 100) -> List[str]:
    return get_store().chunk_text(text, chunk_size=chunk_size, overlap=overlap)


def upsert_embedding(project_id: int, ref_type: str, ref_id: int, content: str) -> None:
    return get_store().upsert_embedding(project_id, ref_type, ref_id, content)


def query_similar(project_id: int, query: str, top_k: int = 5) -> List[Dict]:
    return get_store().query_similar(project_id, query, top_k=top_k)


def search_related_text(project_id: int, query: str, top_k: int = 5) -> List[Dict]:
    return query_similar(project_id=project_id, query=query, top_k=top_k)


__all__ = [
    "upsert_embedding",
    "query_similar",
    "search_related_text",
    "chunk_text",
    "get_store",
    "VectorStore",
]
