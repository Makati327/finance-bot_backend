import os
import chromadb
from sentence_transformers import SentenceTransformer
from app.config import settings

_client = chromadb.PersistentClient(path=settings.CHROMA_PATH)
_collection = _client.get_or_create_collection("finance_tips")
_model = SentenceTransformer(settings.MODEL_NAME)


def load_knowledge_base(file_path: str = "data/tips.txt"):
    if _collection.count() > 0:
        return

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Knowledge base file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        tips = [line.strip() for line in f if line.strip()]

    embeddings = _model.encode(tips).tolist()
    ids = [f"tip_{i}" for i in range(len(tips))]

    _collection.add(
        ids=ids,
        documents=tips,
        embeddings=embeddings,
    )


def retrieve_relevant_tips(query: str, top_k: int = 4):
    query_embedding = _model.encode([query]).tolist()[0]

    results = _collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )

    documents = results.get("documents", [[]])
    if documents and len(documents[0]) > 0:
        return documents[0]
    return []