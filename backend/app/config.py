import os

from dotenv import load_dotenv
load_dotenv()

UPLOAD_DIR="data/uploads"
CHROMA_DIR="data/chroma_db"
LLM_MODEL="gpt-4o"
EMBEDDING_MODEL="text-embedding-3-small"
JUDGE_MODEL = "gpt-4o-mini"
REDIS_URL = os.getenv("REDIS_URL")
DATABASE_URL = os.getenv("DATABASE_URL")
COLLECTION_NAME = "documents"

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINUTES=60