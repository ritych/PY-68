from fastapi import APIRouter, File, UploadFile, HTTPException
from datetime import datetime

from sqlalchemy import select, delete

from database import new_session
from models import Documents, DocumentText
import os

from schemas import NewDocumentsId, DeleteDocumentsId
from tasks import analyze_image

router = APIRouter(
    tags=['PY-68'],
)


@router.post("/upload_doc")
async def upload_doc(file: UploadFile = File(...)) -> NewDocumentsId:
    async with new_session() as session:
        file_bytes = await file.read()
        try:
            if not os.path.exists('documents'):
                os.mkdir('documents')
            with open(f"documents/{file.filename}", "wb") as f:
                f.write(file_bytes)
        except:
            raise HTTPException(status_code=500, detail={'status': 'error', 'id': None})

        new_doc = Documents(
            filename=file.filename,
            date=datetime.utcnow(),
        )
        session.add(new_doc)
        await session.flush()
        await session.commit()
        return {'status': '200', 'id': new_doc.id}


@router.post("/doc_delete")
async def delete_doc(doc_id: int) -> DeleteDocumentsId:
    async with new_session() as session:
        query = select(Documents).filter(Documents.id == doc_id)
        result = await session.execute(query)
        data = result.scalars().all()
        file_path = 'documents/' + data[0].filename
        if os.path.exists(file_path):
            os.remove(file_path)

        stmt = delete(Documents).filter(Documents.id == doc_id)
        await session.execute(stmt)
        await session.commit()

        return {'status': '200', 'message': 'Delete is completed'}


@router.post("/doc_analyse")
async def analyze_doc(doc_id: int):
    async with new_session() as session:
        try:
            query = select(Documents).filter(Documents.id == doc_id)
            result = await session.execute(query)
            data = result.scalars().all()
            filename = data[0].filename

            analyze_image.delay(filename, doc_id)

            return {'status': '200'}
        except:
            return {'status': 'error'}


@router.get("/get_text")
async def get_doc(doc_id: int):
    async with new_session() as session:
        try:
            query = select(DocumentText).filter(DocumentText.id_doc == doc_id)
            result = await session.execute(query)
            data = result.scalars().all()
            text = data[0].text

            return {'status': '200', 'text': text}
        except:
            return {'status': 'error', 'text': None}
