import json
import chromadb
from chromadb.utils import embedding_functions

embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="BAAI/bge-small-en-v1.5"
)

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection(name="majors", embedding_function=embed_fn)

with open("data/majors.json") as f:
    majors = json.load(f)

ids, texts, metas = [], [], []
for m in majors:
    career_lines = []
    for c in m["careers"]:
        if isinstance(c, str):
            career_lines.append(c)
        else:
            line = c["title"]
            if c.get("median_pay"):
                line += f" (median pay ${c['median_pay']:,}"
                if c.get("outlook"):
                    line += f", outlook: {c['outlook']}"
                line += ")"
            career_lines.append(line)

    text = (
        f"{m['label']}: {m['description']} "
        f"Related careers: {'; '.join(career_lines)}. "
        f"Good fit if: {m['good_fit_if']}"
    )

    ids.append(m["key"])
    texts.append(text)
    metas.append({"key": m["key"], "label": m["label"]})

collection.upsert(ids=ids, documents=texts, metadatas=metas)
print(f"Indexed {len(ids)} majors")

# quick test
results = collection.query(
    query_texts=["I love art and want to build things on computers"],
    n_results=3,
)
for meta in results["metadatas"][0]:
    print("-", meta["label"])