from dotenv import load_dotenv

load_dotenv()

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,       # characters (~200 tokens)
    chunk_overlap=160,    # 20% overlap preserves context across boundaries
    separators=["\n\n", "\n", ". ", " "]
)


def chunk_document(text: str, metadata: dict) -> list[dict]:
    """Split a document into overlapping chunks for embedding."""
    chunks = splitter.create_documents([text], metadatas=[metadata])
    return [{"text": chunk.page_content, "metadata": chunk.metadata} for chunk in chunks]


if __name__ == "__main__":
    import os
    kb_path = os.path.join(os.path.dirname(__file__), "..", "data", "knowledge_base.txt")
    text = open(kb_path).read()
    chunks = chunk_document(text, {"source": "knowledge_base.txt"})
    print(f"Document chunked into {len(chunks)} pieces")
    print(f"First chunk ({len(chunks[0]['text'])} chars):")
    print(chunks[0]["text"][:200], "...")
