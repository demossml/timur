from arrow import utcnow, get
from bd.model import Session, Clients
from .util import json_to_xls_format_change, xls_to_json_format_change, he_she_item
from pprint import pprint


name = "📗 Выгрузить данне из базы в формате xls ➡️ "
desc = "Выгружает данне из базы в формате xls"
mime = "file"


class NumberOfLinesInput:
    desc = "Выберите cпособ выгрузки"
    type = "SELECT"

    def get_options(self, session: Session):
        output = [
            {"id": "10", "name": "10 строк ➡️"},
            {"id": "50", "name": "50 строк ➡️"},
            {"id": "100", "name": "100 строк ➡️"},
            {"id": "150", "name": "150 строк ➡️"},
            {"id": "200", "name": "200 строк ➡️"},
            {"id": "250", "name": "250 строк ➡️"},
            {"id": "300", "name": "300 строк ➡️"},
            {"id": "350", "name": "350 строк ➡️"},
            {"id": "400", "name": "400 строк ➡️"},
            {"id": "500", "name": "500 строк ➡️"},
            {"id": "all", "name": "Все строки ➡️"},
        ]

        return output


#             output.append({"id": i, "name": i})


def get_inputs(session: Session):
    return {"lines": NumberOfLinesInput}


def generate(session: Session):
    params = session.params["inputs"]["0"]
    pprint(params)
    if params["lines"] == "all":
        clients = Clients.objects().order_by("closeDate")
    else:
        clients = Clients.objects[0 : int(params["lines"])]().order_by("closeDate")

    data_list = he_she_item(clients)

    pprint(data_list[1])

    book_he = json_to_xls_format_change(data_list[0], "man", data_list[2])

    book_she = json_to_xls_format_change(data_list[1], "woman", data_list[3])

    data_report = [book_he[1], book_she[1]]

    result = data_list[0] + data_list[1]

    for item in result:
        item["closeDate"] = utcnow().shift(hours=3).isoformat()
        Clients.objects(Телефон=item["Телефон"]).update(**item, upsert=True)
    return data_report, book_he[0], book_she[0]
