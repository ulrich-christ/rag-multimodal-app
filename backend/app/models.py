from sqlmodel import SQLModel, Field, DateTime
from datetime import datetime, timezone

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: int | None = Field(default=None,primary_key=True)
    email:str = Field(unique=True,index=True)
    hashed_password :str

    created_at : datetime = Field(default_factory=lambda:datetime.now(timezone.utc))

class UserCreate(SQLModel):
    email:str
    password:str

class UserRead(SQLModel):
    id:int
    email:str


class Document(SQLModel, table=True):
    __tablename__ = "documents"
    id:int | None = Field(default=None, primary_key=True)
    user_id : int = Field(foreign_key="users.id", index=True)
    filename: str
    status:str = "processing"
    chunk_count:int=0
    created_at : datetime=Field(default_factory=lambda:datetime.now(timezone.utc))

class DocumentRead(SQLModel):
    id:int
    filename:str
    status:str
    chunk_count:int
    created_at:datetime