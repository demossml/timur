from arrow import utcnow, get
from bd.model import Session, Clients, PDFFile
from .util import pdf_to_xls
from pprint import pprint
import io


name = "🗂️ БР- Загрузить данные pdf ➡️"
desc = "Загружает данне"
mime = "file_7"


class FileInput:
    name = "Файл"
    desc = "🗃️ Отправте файл в формате  pdf ➡️"
    type = "FILE"


def get_inputs(session: Session):
    return {"file": FileInput}


def generate(session: Session):

    file_data = session.params["inputs"]["0"]["file"]

    result_data = [{"Количество строк": len(file_data)}]

    book = pdf_to_xls(file_data)

    return result_data, book