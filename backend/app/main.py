from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select


from pydantic import BaseModel
import os
from app.config import UPLOAD_DIR
import shutil
from app.ingestion import ingest_file, get_vectorstore
from app.rag import generate_final_answer
from app.database import create_db_and_tables, get_session
from app.models import UserRead, UserCreate, User

from app.auth import hash_password, verify_password, create_access_token, get_current_user


app = FastAPI(title="RAG Multimodal API")

create_db_and_tables()
chat_history = []
db=get_vectorstore()
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/auth/register", response_model=UserRead)
def register(data:UserCreate, session:Session=Depends(get_session)):
    existing = session.exec(select(User).where(User.email==data.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="User Already registered")

    user = User(email=data.email, hashed_password=hash_password(data.password))

    session.add(user)
    session.commit()
    session.refresh(user)

    return user

@app.post("/auth/login")
def login(form:OAuth2PasswordRequestForm=Depends(), session:Session=Depends(get_session) ):

    user = session.exec(select(User).where(User.email==form.username)).first()

    if user is None or not verify_password(form.password,user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    return {"access_token": create_access_token(user_id=user.id), "token_type":"bearer"}


@app.get("/auth/me", response_model=UserRead)
def me(current_user:User = Depends(get_current_user)):
    return current_user



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