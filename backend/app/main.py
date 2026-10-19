from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.tasks import ingestion_document_task

from pydantic import BaseModel
import os
from app.config import UPLOAD_DIR
import shutil
from app.ingestion import ingest_file, get_vectorstore
from app.rag import generate_final_answer
from app.database import create_db_and_tables, get_session
from app.models import UserRead, UserCreate, User, Document, DocumentRead

from app.auth import hash_password, verify_password, create_access_token, get_current_user


app = FastAPI(title="RAG Multimodal API")

create_db_and_tables()
chat_histories = {}
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



@app.post("/documents", response_model=DocumentRead)
def upload_file(file:UploadFile=File(...), current_user:User = Depends(get_current_user), session:Session=Depends(get_session)):
    filename = os.path.basename(file.filename)

    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400,detail="Only PDF files are accepted")

    doc = Document(user_id=current_user.id, filename=filename)
    session.add(doc)
    session.commit()
    session.refresh(doc)

    user_dir = os.path.join(UPLOAD_DIR, str(current_user.id))
    os.makedirs(user_dir, exist_ok=True)
    file_path=os.path.join(user_dir, f"{doc.id}_{filename}")

    with open(file_path, 'wb') as buffer:
        shutil.copyfileobj(file.file,buffer)

    ingestion_document_task.delay(doc.id, file_path)
    return doc



@app.get("/documents/{document_id}", response_model=DocumentRead)
def list_documents(document_id:int,current_user:User = Depends(get_current_user), session:Session=Depends(get_session)):
    doc = session.get(Document, document_id)
    if doc is None:
            raise HTTPException(status_code=404, detail="Document Not found")
    if doc.user_id != current_user.id:
             raise HTTPException(status_code=403, detail="Not Your Documents")
    if doc.status != "ready":
             raise HTTPException(status_code=400, detail="Documents not ready Yet")
    return doc

class ChatRequest(BaseModel):
    document_id:int
    question:str

@app.post("/chat")
def chat(req:ChatRequest,current_user:User = Depends(get_current_user), session:Session=Depends(get_session)):
    history = chat_histories.setdefault((current_user.id, req.document_id), [])
    doc = session.get(Document, req.document_id)
    if doc is None:
         raise HTTPException(status_code=404, detail="Document Not found")
    if doc.user_id != current_user.id:
         raise HTTPException(status_code=403, detail="Not Your Documents")
    if doc.status != "ready":
         raise HTTPException(status_code=400, detail="Documents not ready Yet")
    response=generate_final_answer(db,req.question,chat_history=history,document_id=doc.id)
    return response