import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import chromadb
from chromadb.utils import embedding_functions

load_dotenv()
MODEL_NAME = os.getenv("MODEL_NAME")
SERVER_URL = os.getenv("SERVER_URL", "http://localhost:1234/v1")

llm = OpenAI(base_url=SERVER_URL, api_key="not-needed")

embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="BAAI/bge-small-en-v1.5"
)
db = chromadb.PersistentClient(path="chroma_db")
majors_col = db.get_collection("majors", embedding_function=embed_fn)
schools_col = db.get_collection("schools", embedding_function=embed_fn)

SYSTEM_PROMPT = """You are a friendly college and major advisor for high school students.

Rules:
- Use ONLY the MAJORS and SCHOOLS data provided below for facts, numbers, and school names. Never invent schools, costs, or statistics.
- If the data doesn't cover something, say so honestly.
- If you don't yet know the student's interests, favorite classes, strengths, budget, or preferred location, ask 1-2 short questions first.
- Once you know enough, suggest 3-5 majors with a short "why this fits you" for each, then a few schools with their net price, graduation rate, and website.
- When you cite earnings, mention they are for students who received federal aid.
- Remind students this is a guide, not a replacement for a school counselor.
- Keep answers clear and friendly, not too long."""

app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]
    state: str | None = None          # e.g. "CA"
    max_net_price: int | None = None  # e.g. 20000


def build_filter(state, max_net_price):
    conditions = []
    if state:
        conditions.append({"state": state.upper()})
    if max_net_price:
        conditions.append({"net_price": {"$gt": 0}})
        conditions.append({"net_price": {"$lte": max_net_price}})
    if not conditions:
        return None
    return conditions[0] if len(conditions) == 1 else {"$and": conditions}


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_NAME}


@app.post("/chat-mock")
def chat_mock(req: ChatRequest):
    return {
        "reply": "This is a fake reply so the UI can be built. Biology and Visual Arts could be a great fit!",
        "sources": {
            "majors": ["Biology", "Visual and Performing Arts"],
            "schools": ["Example University"],
        },
        "school_cards": [
            {
                "name": "Example University", "city": "Santa Cruz", "state": "CA",
                "ownership": "public school", "net_price": 15000,
                "grad_rate": 0.7, "earnings": 50000,
                "website": "https://example.edu",
            }
        ],
        "model": "mock",
    }


@app.post("/chat")
def chat(req: ChatRequest):
    user_texts = [m.content for m in req.messages if m.role == "user"]
    query = " ".join(user_texts[-3:])

    # 1. find fitting majors
    major_res = majors_col.query(query_texts=[query], n_results=4)
    major_docs = major_res["documents"][0]
    major_labels = [m["label"] for m in major_res["metadatas"][0]]

    # 2. find schools strong in those majors, with optional filters
    school_query = f"{query}. Strong programs in: {', '.join(major_labels[:3])}"
    school_res = schools_col.query(
        query_texts=[school_query],
        n_results=5,
        where=build_filter(req.state, req.max_net_price),
    )
    school_docs = school_res["documents"][0]
    school_cards = school_res["metadatas"][0]

    context = (
        "MAJORS:\n" + "\n".join(f"- {d}" for d in major_docs)
        + "\n\nSCHOOLS:\n" + "\n".join(f"- {d}" for d in school_docs)
    )

    messages = [{"role": "system", "content": SYSTEM_PROMPT + "\n\n" + context}]
    messages += [{"role": m.role, "content": m.content} for m in req.messages]

    response = llm.chat.completions.create(
        model=MODEL_NAME, messages=messages, temperature=0.4
    )

    return {
        "reply": response.choices[0].message.content,
        "sources": {
            "majors": major_labels,
            "schools": [c["name"] for c in school_cards],
        },
        "school_cards": school_cards,
        "model": MODEL_NAME,
    }