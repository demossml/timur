from arrow import utcnow, get
from bd.model import Session, Clients, PDFFile
from .util import json_to_xls_format_change, he_she
from pprint import pprint
import io


name = "🗂️ Загрузить данные zip/rar-pdf ➡️"
desc = "Загружает данне"
mime = "file"


class FileInput:
    name = "Файл"
    desc = "🗃️ Отправте файл в формате zip/rar c pdf ➡️"
    type = "FILE"


def get_inputs(session: Session):
    return {"file": FileInput}


def generate(session: Session):
    params = session.params["inputs"]["0"]
    result_data = []

    data_list = he_she(params["file"])

    # pprint(he_she(params["file"][1]))

    book_he = json_to_xls_format_change(data_list[0], "man", data_list[2])

    book_she = json_to_xls_format_change(data_list[1], "woman", data_list[3])

    data_report = [book_he[1], book_she[1]]

    for item in params["file"]:
        item["closeDate"] = utcnow().isoformat()
        Clients.objects(Телефон=item["Телефон"]).update(**item, upsert=True)
        result_data.append(item)
    return data_report, [book_he[0], book_she[0]]
