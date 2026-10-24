import json
import chromadb
from chromadb.utils import embedding_functions

embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="BAAI/bge-small-en-v1.5"
)

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection(name="schools", embedding_function=embed_fn)

with open("data/documents.json") as f:
    docs = json.load(f)

BATCH = 200
for i in range(0, len(docs), BATCH):
    batch = docs[i:i + BATCH]
    collection.upsert(
        ids=[d["id"] for d in batch],
        documents=[d["text"] for d in batch],
        metadatas=[d["metadata"] for d in batch],
    )
    print(f"Indexed {min(i + BATCH, len(docs))} / {len(docs)}")
