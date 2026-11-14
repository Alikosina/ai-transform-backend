import logging
from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "alik_sloyan_profile.txt"
PERSIST_DIR = Path(__file__).resolve().parent.parent.parent / "chroma_db"
COLLECTION_NAME = "alik_sloyan_profile"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

_embeddings: FastEmbedEmbeddings | None = None
_vectorstore: Chroma | None = None
# Set once RAG fails (e.g. the embedding model cannot be downloaded), so we
# don't retry the slow download on every chat request.
_rag_disabled = False


def get_vectorstore() -> Chroma:
    global _vectorstore, _embeddings
    if _vectorstore is not None:
        return _vectorstore

    # Model is loaded lazily on first use, not at import time.
    if _embeddings is None:
        _embeddings = FastEmbedEmbeddings(model_name=EMBEDDING_MODEL)

    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=_embeddings,
        persist_directory=str(PERSIST_DIR),
    )

    if not vectorstore.get()["ids"]:
        text = DATA_PATH.read_text(encoding="utf-8")
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_text(text)
        vectorstore.add_texts(chunks)

    _vectorstore = vectorstore
    return _vectorstore


def retrieve_context(query: str, k: int = 3) -> str:
    global _rag_disabled
    if _rag_disabled:
        return ""
    try:
        results = get_vectorstore().similarity_search(query, k=k)
    except Exception:
        # Embedding model unavailable: answer without RAG context instead of failing the request.
        logger.exception("RAG retrieval disabled; answering without context")
        _rag_disabled = True
        return ""
    return "\n\n".join(doc.page_content for doc in results)
