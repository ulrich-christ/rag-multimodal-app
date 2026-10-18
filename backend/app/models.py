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