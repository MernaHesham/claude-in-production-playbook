from dotenv import load_dotenv
import chromadb
import anthropic
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

load_dotenv()
client = anthropic.Anthropic()
chroma = chromadb.Client()
embedder = SentenceTransformerEmbeddingFunction("all-MiniLM-L6-v2")

collection = chroma.get_or_create_collection(
    name="knowledge_base",
    embedding_function=embedder
)

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=160)


def chunk_document(text: str, metadata: dict) -> list[dict]:
    chunks = splitter.create_documents([text], metadatas=[metadata])
    return [{"text": c.page_content, "metadata": c.metadata} for c in chunks]


def ingest_document(text: str, doc_id: str, metadata: dict = None):
    """Chunk and embed a document into the vector store."""
    chunks = chunk_document(text, metadata or {})
    collection.add(
        documents=[c["text"] for c in chunks],
        ids=[f"{doc_id}-{i}" for i, _ in enumerate(chunks)],
        metadatas=[c["metadata"] for c in chunks]
    )
    print(f"Ingested {len(chunks)} chunks from {doc_id}")


def rag_query(question: str, n_results: int = 5) -> str:
    """Retrieve relevant chunks and ask Claude to answer."""
    results = collection.query(query_texts=[question], n_results=n_results)
    context_chunks = results["documents"][0]

    context_text = "\n\n---\n\n".join([
        f"[Source {i+1}]\n{chunk}"
        for i, chunk in enumerate(context_chunks)
    ])

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system="""Answer questions using ONLY the context provided.
Cite sources as [Source N]. If the answer is not in the context, say so clearly.""",
        messages=[{"role": "user", "content": f"<context>\n{context_text}\n</context>\n\n<question>{question}</question>"}]
    )
    return response.content[0].text


if __name__ == "__main__":
    import os
    kb_path = os.path.join(os.path.dirname(__file__), "..", "data", "knowledge_base.txt")
    text = open(kb_path).read()
    ingest_document(text, "knowledge_base", {"source": "knowledge_base.txt"})
    answer = rag_query("What are the support SLAs for Enterprise customers?")
    print(answer)
