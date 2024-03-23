from arrow import utcnow, get
from bd.model import Session, Clients
from .util import json_to_xls_format_change, xls_to_json_format_change
from pprint import pprint


name = "Выгрузить данные"
desc = "Выгружает данне из базы в формате xls"
mime = "file"


class UploadInput:
    desc = "Выберите cпособ выгрузки"
    type = "SELECT"

    def get_options(self, session: Session):
        output = [
            {"id": "upload", "name": "Выгрузка без исползования фильтров"},
            {"id": "upload_filter", "name": "Выгрузка c исползованием фильтров"},
        ]

        return output


class NumberOfLinesInput:
    desc = "Выберите cпособ выгрузки"
    type = "SELECT"

    def get_options(self, session: Session):
        output = [
            {"id": "10", "name": "10 строк"},
            {"id": "50", "name": "50 строк"},
            {"id": "100", "name": "100 строк"},
            {"id": "150", "name": "150 строк"},
            {"id": "200", "name": "200 строк"},
            {"id": "250", "name": "250 строк"},
            {"id": "300", "name": "300 строк"},
            {"id": "350", "name": "350 строк"},
            {"id": "400", "name": "400 строк"},
            {"id": "500", "name": "500 строк"},
            {"id": "all", "name": "Все строки"},
        ]

        return output


class SelectionCriterionInput:
    name = "Группа товаров"
    desc = "Выберите критерии отбора"
    type = "file"

    def get_options(self, session: Session):
        clients = Clients.objects()

        output = []
        result = []
        for item in clients:
            for element in item:
                if element not in result:
                    if element != "id":
                        result.append(element)
        for i in result:
            output.append({"id": i, "name": i})


def get_inputs(session: Session):
    return {"lines": NumberOfLinesInput}


def generate(session: Session):
    params = session.params["inputs"]["0"]
    if params["lines"] == "all":
        clients = Clients.objects().order_by("closeDate")
    else:
        clients = Clients.objects[0 : int(params["lines"])]().order_by("closeDate")
    output = []
    not_in = ["id", "Пол", "Т", "ТИП", "Продукт"]
    for item in clients:
        dict_ = {}
        for key in item:
            if key not in not_in:
                dict_[key] = item[key]
        output.append(dict_)

    pprint(output)
    book = json_to_xls_format_change(output)

    book.save("result77.xlsx")
    result = xls_to_json_format_change(book)
    for item in result:
        item["closeDate"] = utcnow().shift(hours=3).isoformat()
        Clients.objects(Телефон=item["Телефон"]).update(**item, upsert=True)
    return [{"Выгружено строк": params["lines"]}]
