from datetime import datetime

from pydantic import BaseModel


class DocumentsOrm(BaseModel):
    id: int
    filename: str
    date: datetime


class DocumentsTextOrm(BaseModel):
    id: int
    id_doc: int
    text: str


class NewDocumentsId(BaseModel):
    status: str
    id: int


class DeleteDocumentsId(BaseModel):
    status: str
    message: str


class GetDocumentsText(BaseModel):
    status: str
    text: str
