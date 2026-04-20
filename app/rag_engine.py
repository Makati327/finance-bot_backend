from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from app.config import settings
import os

client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
)

model = SentenceTransformer(settings.MODEL_NAME)
COLLECTION_NAME = settings.QDRANT_COLLECTION


def ensure_collection():
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )


def load_knowledge_base(file_path: str = "data/tips.txt"):
    ensure_collection()

    count = client.count(collection_name=COLLECTION_NAME).count
    if count > 0:
        return

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Knowledge base file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        tips = [line.strip() for line in f if line.strip()]

    embeddings = model.encode(tips).tolist()

    points = [
        PointStruct(
            id=i,
            vector=embeddings[i],
            payload={"text": tips[i]}
        )
        for i in range(len(tips))
    ]

    client.upsert(collection_name=COLLECTION_NAME, points=points)


def retrieve_relevant_tips(query: str, top_k: int = 4):
    query_vector = model.encode(query).tolist()

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
    )

    return [point.payload["text"] for point in results.points] # type: ignore