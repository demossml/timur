from arrow import utcnow, get
from bd.model import Session, Clients, PDFFile
from .util import json_to_xls_format_change
from pprint import pprint
import io


name = "🗂️ Загрузить данные  zip-pdf ➡️"
desc = "Загружает данне"
mime = "file"


class FileInput:
    name = "Файл"
    desc = "📂 Отправте файл в формате zip c pdf ➡️"
    type = "FILE"


def get_inputs(session: Session):
    return {"file": FileInput}


def generate(session: Session):
    params = session.params["inputs"]["0"]
    result_data = []

    book = json_to_xls_format_change(params["file"])
    binary_stream = io.BytesIO()
    book.save(binary_stream)
    binary_stream.seek(0)

    for item in params["file"]:
        item["closeDate"] = utcnow().isoformat()
        Clients.objects(Телефон=item["Телефон"]).update(**item, upsert=True)
        result_data.append(item)

    return [{"Выгружено строк": len(params["file"])}], binary_stream
