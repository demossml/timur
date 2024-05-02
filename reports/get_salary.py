from bd.model import Clients, Document
from arrow import utcnow, get
from bd.model import Session, Clients, Documents
from .util import xls_to_json_format_change, json_to_xls_format_change_
from pprint import pprint
from openpyxl import load_workbook, Workbook
from openpyxl.utils import get_column_letter, get_column_letter
import sys  # Импортируем модуль sys для получения информации о текущем исключении
from decimal import Decimal


name = "🤑🤑🤑 Зарплата ➡️".upper()
desc = "Загружает данне из xls в базу"
mime = "file_5"


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
    try:
        # Получаем параметры сессии
        params = session.params["inputs"]["0"]
        # pprint(params)
        # Создаем словарь для данных CRM
        crm_dict = {}

        # Создаем словарь CRM, где ключ - оператор, значение - список ID заказов
        for item in params["CRM"]:
            operator = item.get("Оператор")
            if operator not in crm_dict:
                crm_dict[operator] = []
            crm_dict[operator].append(item.get("ID"))
        # pprint(crm_dict)

        # Получаем ключи первого элемента списка Cdek
        keys = list(params["Cdek"][0].keys())

        # Получаем первый и второй ключи из Cdek
        key1 = keys[0]
        key2 = keys[1]

        # Создаем словарь  для каждого заказа из Cdek
        cdek_date = {
            item[key1]: item[key2]
            for item in params["Cdek"]
            if None not in (item.get(key1), item.get(key2))
        }

        # pprint(cdek_date)
        # Создаем словари для сумм продаж, списка заказов и данных о заказах
        dict_sales = {}
        dict_order = {}
        dict_order_list_ = {}

        # Обрабатываем данные для каждого пользователя CRM
        for user, order_list in crm_dict.items():
            sum_ = 0
            order_ = {}
            order_list_ = []

            # Обходим список заказов для каждого оператора
            for order in order_list:
                # Проверяем наличие данных о заказе в Cdek
                if order in cdek_date:
                    order_list_.append(order)
                    order_.update({str(order): cdek_date.get(order, 0)})

                sum_ += cdek_date.get(order, 0)

            # Заполняем словари данными
            dict_sales.update({user: sum_})
            dict_order.update({user: order_})
            dict_order_list_.update({user: order_list_})

        # Извлекаем данные о файлах из параметров сессии ProvidedFile
        provided_file_ = params["ProvidedFile"]

        provided_file = []

        oldest_salesman_data = {}

        preoldest_salesman_list = ["POD", "SKP", "UDL", "M31"]

        # Заменяем значения None на 0 в каждом словаре
        # Итерируемся по элементам списка provided_file_
        for item in provided_file_:
            # Проверяем, есть ли текущий сотрудник в списке preoldest_salesman_list
            if item["Сотрудник"] in preoldest_salesman_list:
                # Если сотрудник является одним из старейших, создаем новый словарь new_item,
                # где заменяем значения None на 0
                new_item = {
                    key: (value if value is not None else 0)
                    for key, value in item.items()
                }

                # Обновляем словарь oldest_salesman_data, используя имя сотрудника в качестве ключа
                # и новый словарь new_item в качестве значения
                oldest_salesman_data.update({item["Сотрудник"]: new_item})
            else:
                # Если сотрудник не является старейшим, также создаем новый словарь new_item,
                # где заменяем значения None на 0
                new_item = {
                    key: (value if value is not None else 0)
                    for key, value in item.items()
                }
                # Добавляем новый словарь new_item в исходный список provided_file_
                provided_file.append(new_item)
        pprint(oldest_salesman_data)
        # Инициализируем переменные для общей суммы и списка данных
        total_date = []
        total_sum = 0

        # Обходим данные из файла
        for item in provided_file:
            if item["Сотрудник"] != 0:
                try:
                    # pprint(item["Сотрудник"])

                    # pprint(dict_sales.get(item["Сотрудник"], 0))
                    # Вычисляем общую сумму для каждого сотрудника
                    total = (
                        (
                            Decimal(str(dict_sales.get(item["Сотрудник"], 0)))
                            * Decimal(str(item["%"]))
                        )
                        + Decimal(str(item["Оклад"]))
                        + Decimal(str(item["Отпускные"]))
                        - Decimal(str(item["Офчасть"]))
                        - Decimal(str(item["Долг"]))
                        + Decimal(str(item["доп премия"]))
                    )
                    total = total.quantize(Decimal("0.00"))
                    total_sum += total

                    # Формируем результаты для записи
                    result = {
                        "Сотрудник": item["Сотрудник"],
                        "Сумма": Decimal(dict_sales.get(item["Сотрудник"], 0)).quantize(
                            Decimal("0.00")
                        ),
                        "%": (Decimal(item["%"]) * 100).quantize(Decimal("0.00")),
                        "Итог%": (
                            Decimal(dict_sales.get(item["Сотрудник"], 0))
                            * Decimal(item["%"])
                        ).quantize(Decimal("0.00")),
                        "Оклад": Decimal(item["Оклад"]).quantize(Decimal("0.00")),
                        "Отпускные": Decimal(item["Отпускные"]).quantize(
                            Decimal("0.00")
                        ),
                        "Офчасть": Decimal(item["Офчасть"]).quantize(Decimal("0.00")),
                        "Долг": Decimal(item["Долг"]).quantize(Decimal("0.00")),
                        "доп премия": Decimal(item["доп премия"]).quantize(
                            Decimal("0.00")
                        ),
                        "Итог": total,
                    }

                    total_date.append(result)
                    result_up = {}
                    result_up.update(result)

                    # Форматируем заказы для записи
                    format_order = {}
                    if item["Сотрудник"] in dict_order:
                        for k, v in dict_order[item["Сотрудник"]].items():
                            # pprint(type(k))
                            # pprint(k)

                            format_order.update({str(k): v})

                    result.update(format_order)

                    # pprint(format_order)

                    # Добавляем дополнительные данные для записи
                    result_up.update(
                        {
                            "closeDate": utcnow().shift(hours=3).isoformat(),
                            "order_list": dict_order_list_.get(item["Сотрудник"], []),
                            "order": dict_order.get(item["Сотрудник"], {}),
                        }
                    )

                    # pprint(result_up)
                    # Обновление документов в базе данных
                    Documents.objects(closeDate=result_up["closeDate"]).update(
                        **result_up, upsert=True
                    )
                except Exception as e:
                    print(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")

        prefix = ["POD", "SKP", "UDL", "M31"]

        # Создаем словарь, где ключи - префиксы, значения - список элементов
        prefix_dict: dict = {p: [] for p in prefix}

        # Заполняем префиксный словарь
        for item in total_date:
            for p in prefix:
                if item["Сотрудник"].startswith(
                    p
                ):  # Проверяем, начинается ли значение ключа "Сотрудник" с текущего префикса
                    prefix_dict[p].append(
                        item
                    )  # Если да, добавляем элемент в список, соответствующий текущему префиксу

        for (
            pref,
            list_,
        ) in prefix_dict.items():  # Перебираем ключи и значения в словаре prefix_dict
            sum_items = 0
            for item in list_:
                sum_items += Decimal(item["Сумма"]).quantize(
                    Decimal("0.00")
                )  # Считаем сумму значений ключа "Сумма" для всех элементов списка

            total_ = Decimal(
                (sum_items * oldest_salesman_data[pref]["%"])
                + oldest_salesman_data[pref]["Оклад"]
                + oldest_salesman_data[pref]["Отпускные"]
                - oldest_salesman_data[pref]["Офчасть"]
                - oldest_salesman_data[pref]["Долг"]
                + oldest_salesman_data[pref]["доп премия"]
            ).quantize(Decimal("0.00"))
            resut = {
                "%": Decimal(oldest_salesman_data[pref]["%"] * 100).quantize(
                    Decimal("0.00")
                ),
                "Долг": Decimal(oldest_salesman_data[pref]["Долг"]).quantize(
                    Decimal("0.00")
                ),
                "Итог": total_,
                "Итог%": Decimal(
                    sum_items * oldest_salesman_data[pref]["Итог%"]
                ).quantize(Decimal("0.00")),
                "Оклад": Decimal(oldest_salesman_data[pref]["Оклад"]).quantize(
                    Decimal("0.00")
                ),
                "Отпускные": Decimal(oldest_salesman_data[pref]["Отпускные"]).quantize(
                    Decimal("0.00")
                ),
                "Офчасть": Decimal(oldest_salesman_data[pref]["Офчасть"]).quantize(
                    Decimal("0.00")
                ),
                "Сотрудник": pref,
                "Сумма": Decimal(sum_items).quantize(Decimal("0.00")),
                "доп премия": Decimal(
                    oldest_salesman_data[pref]["доп премия"]
                ).quantize(Decimal("0.00")),
            }
            list_.append(resut)  # Изменил способ создания словаря
            total_date.append(resut)

        # pprint(prefix_dict)

        # Форматируем данные для экспорта в Excel и добавляем в список книг
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
        # pprint(books)

        # Возвращаем данные и книги Excel
        return total_date, books
    except Exception as e:
        print(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")
