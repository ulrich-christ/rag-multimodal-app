from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import os
from app.config import UPLOAD_DIR
import shutil
from app.ingestion import ingest_file, get_vectorstore
from app.rag import generate_final_answer

app = FastAPI(title="RAG Multimodal API")
chat_history = []
db=get_vectorstore()
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/documents")
def upload_file(file:UploadFile=File(...)):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filename = os.path.basename(file.filename)

    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400,detail="Only PDF files are accepted")

    file_path=os.path.join(UPLOAD_DIR,filename)


    with open(file_path, 'wb') as buffer:
        shutil.copyfileobj(file.file,buffer)


    nb_docs=ingest_file(file_path=file_path)

    return {
        "filename": filename, "chunk_count":nb_docs
    }

class ChatRequest(BaseModel):
    question:str

@app.post("/chat")
def chat(req:ChatRequest):
    response=generate_final_answer(db,req.question,chat_history=chat_history)
    return response