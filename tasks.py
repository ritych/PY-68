from celery import Celery
from PIL import Image
import pytesseract
import cv2
import os

from database import session
from models import DocumentText

celery = Celery('tasks', backend='redis://127.0.0.1:6379', broker='redis://127.0.0.1:6379')


@celery.task
def analyze_image(image_filename: str, doc_id: int):
    image = 'documents/' + image_filename
    preprocess = "thresh"
    image = cv2.imread(image)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if preprocess == "thresh":
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    filename = "documents/" + "{}.png".format(os.getpid())
    cv2.imwrite(filename, gray)

    try:
        text = pytesseract.image_to_string(Image.open(filename))

        new_doc = DocumentText(id_doc=doc_id, text=text)
        session.add(new_doc)
        session.commit()
        os.remove(filename)
        return True
    except:
        os.remove(filename)
        return False
