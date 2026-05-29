import chromadb
import hashlib
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

embedder = SentenceTransformerEmbeddingFunction("all-MiniLM-L6-v2")
db = chromadb.Client()
col = db.get_or_create_collection("research", embedding_function=embedder)


def _chunk(text: str, size: int = 400, overlap: int = 80) -> list[str]:
    words, chunks, i = text.split(), [], 0
    while i < len(words):
        chunks.append(" ".join(words[i: i + size]))
        i += size - overlap
    return chunks


def ingest(url: str, text: str) -> int:
    chunks = _chunk(text)
    ids = [hashlib.md5(f"{url}-{i}".encode()).hexdigest() for i in range(len(chunks))]
    metas = [{"url": url, "chunk": i} for i in range(len(chunks))]
    col.upsert(documents=chunks, ids=ids, metadatas=metas)
    return len(chunks)


def retrieve(query: str, k: int = 5) -> list[dict]:
    res = col.query(query_texts=[query], n_results=k)
    return [
        {"text": doc, "url": meta["url"]}
        for doc, meta in zip(res["documents"][0], res["metadatas"][0])
    ]
