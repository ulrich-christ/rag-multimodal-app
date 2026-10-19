from celery import Celery
from app.config import REDIS_URL

celery_app = Celery("rag", broker=REDIS_URL, include=["app.tasks"])