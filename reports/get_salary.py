from bd.model import Clients, Document
from arrow import utcnow, get
from bd.model import Session, Clients, Documents
from .util import xls_to_json_format_change, json_to_xls_format_change_
from pprint import pprint
from openpyxl import load_workbook, Workbook
from openpyxl.utils import get_column_letter, get_column_letter


name = "🤑🤑🤑 Зарплата ➡️".upper()
desc = "Загружает данне из xls в базу"
mime = "file"


class FileCRMInput:
    name = "Файл CRM"
    desc = "Отправте файл CRM  в формате xlsx"
    type = "FILE"


class FileCdekInput:
    name = "Файл cdek"
    desc = "Отправте файл cdek в формате xlsx"
    type = "FILE"


class FileProvidedFileInput:
    name = "Файл provided file"
    desc = "Отправте предоставляемый файл в формате xlsx"
    type = "FILE"


def get_inputs(session: Session):
    return {
        "CRM": FileCRMInput,
        "Cdek": FileCdekInput,
        "ProvidedFile": FileProvidedFileInput,
    }


def generate(session: Session):

    params = session.params["inputs"]["0"]
    crm_dict = {}

    for item in params["CRM"]:
        operator = item.get("Оператор")
        if operator not in crm_dict:
            crm_dict[operator] = []
        crm_dict[operator].append(item.get("ID"))

    keys = list(params["Cdek"][0].keys())

    key1 = keys[0]
    key2 = keys[1]

    cdek_date = {item[key1]: item[key2] for item in params["Cdek"]}

    dict_sales = {}
    dict_order = {}
    dict_order_list_ = {}
    for user, order_list in crm_dict.items():
        sum_ = 0
        order_ = {}
        order_list_ = []
        for order in order_list:
            if order in cdek_date:
                order_list_.append(order)
                order_.update({str(order): cdek_date.get(order, 0)})

            sum_ += cdek_date.get(order, 0)

        dict_sales.update({user: sum_})
        dict_order.update({user: order_})
        dict_order_list_.update({user: order_list_})

    provided_file = params["ProvidedFile"]
    # Заменяем значения None на 0 в каждом словаре
    for item in provided_file:
        item.update((key, 0) for key, value in item.items() if value is None)

    total_date = []
    total_sum = 0
    for item in params["ProvidedFile"]:
        if item["Сотрудник"] != 0:
            total = (
                (dict_sales.get(item["Сотрудник"], 0) * item["%"])
                + item["Оклад"]
                + item["Отпускные"]
                - item["Офчасть"]
                - item["Долг"]
                + item["доп премия"]
            )
            total_sum += total
            result = {
                "Сотрудник": item["Сотрудник"],
                "Сумма": dict_sales.get(item["Сотрудник"], 0),
                "%": item["%"] * 100,
                "Итог%": dict_sales.get(item["Сотрудник"], 0) * item["%"],
                "Оклад": item["Оклад"],
                "Отпускные": item["Отпускные"],
                "Офчасть": item["Офчасть"],
                "Долг": item["Долг"],
                "доп премия": item["доп премия"],
                "Итог": total,
            }

            total_date.append(result)
            result_up = {}
            result_up.update(result)

            format_order = {}
            for k, v in dict_order[item["Сотрудник"]].items():
                format_order.update({str(k): v})

            result.update(format_order)
            # pprint(item["Сотрудник"])
            # pprint(dict_order[item["Сотрудник"]])
            result_up.update(
                {
                    "closeDate": utcnow().shift(hours=3).isoformat(),
                    "order_list": dict_order_list_[item["Сотрудник"]],
                    "order": dict_order[item["Сотрудник"]],
                }
            )

            Documents.objects(closeDate=result_up["closeDate"]).update(
                **result_up, upsert=True
            )
    prefix = ["POD_", "SKP_", "UDL_", "M31_"]

    # Initialize a dictionary to store lists based on prefix
    prefix_dict: dict = {p: [] for p in prefix}

    # Iterate over the date list and append each element to the corresponding list in prefix_dict
    for item in total_date:
        for p in prefix:
            if item["Сотрудник"].startswith(p):
                prefix_dict[p].append(item)

    books = []
    for k, v in prefix_dict.items():
        if len(v) > 0:
            books.append(json_to_xls_format_change_(v))
    total_date.append(
        {
            "closeDate": utcnow().shift(hours=3).isoformat()[:10],
            "Итог": total_sum,
        }
    )
    return total_date, books
