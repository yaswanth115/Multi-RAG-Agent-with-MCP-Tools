from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from backend.graph import graph
from backend.document_processor import extract_text, chunk_text
from backend.vector_store import vector_store
from backend.hybrid_search import hybrid_search
import shutil
import os
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Request Model for /query
# ----------------------------
class QueryRequest(BaseModel):
    query: str
    session_id: str | None = "default"


# ----------------------------
# Upload Endpoint
# ----------------------------
@app.post("/upload")
async def upload(file: UploadFile = File(...)):

    path = f"temp_{file.filename}"

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = extract_text(path)
    chunks = chunk_text(text)

    vector_store.add_documents(chunks)
    hybrid_search.build(chunks)

    os.remove(path)

    return {"message": "Document processed successfully"}


# ----------------------------
# Query Endpoint
# ----------------------------
@app.post("/query")
async def query(data: QueryRequest):

    state = {
        "query": data.query,
        "session_id": data.session_id
    }

    result = graph.invoke(state)

    return {
        "answer": result.get("answer"),
        "source": result.get("source")
    }
