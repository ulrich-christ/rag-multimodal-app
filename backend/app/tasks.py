from sqlmodel import Session
from app.celery_app import celery_app
from app.database import engine

from app.models import Document
from app.ingestion  import ingest_file

@celery_app.task
def ingestion_document_task(document_id:int,file_path:str):
    with Session(engine) as session:
        doc = session.get(Document,document_id)
        if doc is None:
            return
        doc.status = "processing"
        session.add(doc)
        session.commit()

        try:
            doc.chunk_count = ingest_file(file_path=file_path, user_id=doc.user_id, document_id=doc.id)
            doc.status = "ready"
        except Exception as e:
            print(f"Ingestion Failed for document {document_id}: {e}")
            doc.status="failed"

        session.add(doc)
        session.commit()

        return doc
