from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "alik_sloyan_profile.txt"
PERSIST_DIR = Path(__file__).resolve().parent.parent.parent / "chroma_db"
COLLECTION_NAME = "alik_sloyan_profile"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

_embeddings = FastEmbedEmbeddings(model_name=EMBEDDING_MODEL)
_vectorstore: Chroma | None = None


def get_vectorstore() -> Chroma:
    global _vectorstore
    if _vectorstore is not None:
        return _vectorstore

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
    results = get_vectorstore().similarity_search(query, k=k)
    return "\n\n".join(doc.page_content for doc in results)
