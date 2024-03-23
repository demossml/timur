from bd.model import Session
from arrow import utcnow, get
from typing import List, Tuple
from pprint import pprint


from openpyxl import Workbook
from openpyxl.utils import get_column_letter


# Принимает словарь с данными о продукте


def period_to_date(period: str) -> utcnow:
    """
    :param period: day, week,  fortnight, month, two months,
    :return: utcnow - period
    """
    if period == "day":
        return utcnow().to("local").replace(hour=3, minute=00).isoformat()
    if period == "week":
        return (
            utcnow().to("local").shift(days=-7).replace(hour=3, minute=00).isoformat()
        )
    if period == "fortnight":
        return (
            utcnow().to("local").shift(days=-14).replace(hour=3, minute=00).isoformat()
        )
    if period == "month":
        return (
            utcnow().to("local").shift(months=-1).replace(hour=3, minute=00).isoformat()
        )
    if period == "two months":
        return (
            utcnow().to("local").shift(months=-2).replace(hour=3, minute=00).isoformat()
        )
    if period == "6 months":
        return (
            utcnow().to("local").shift(months=-6).replace(hour=3, minute=00).isoformat()
        )
    if period == "12 months":
        return (
            utcnow()
            .to("local")
            .shift(months=-12)
            .replace(hour=3, minute=00)
            .isoformat()
        )
    if period == "24 months":
        return (
            utcnow()
            .to("local")
            .shift(months=-24)
            .replace(hour=3, minute=00)
            .isoformat()
        )
    if period == "48 months":
        return (
            utcnow()
            .to("local")
            .shift(months=-48)
            .replace(hour=3, minute=00)
            .isoformat()
        )
    raise Exception("Period is not supported")


def period_to_date_2(period: str) -> utcnow:
    """
    :param period: day, week,  fortnight, month, two months,
    :return: utcnow + period
    """
    if period == "day":
        return utcnow().replace(hour=3, minute=00).isoformat()
    if period == "week":
        return utcnow().shift(days=7).replace(hour=3, minute=00).isoformat()
    if period == "fortnight":
        return utcnow().shift(days=14).replace(hour=3, minute=00).isoformat()
    if period == "month":
        return utcnow().shift(months=1).replace(hour=3, minute=00).isoformat()
    if period == "two months":
        return utcnow().shift(months=2).replace(hour=3, minute=00).isoformat()
    if period == "6 months":
        return utcnow().shift(months=6).replace(hour=3, minute=00).isoformat()
    if period == "12 months":
        return utcnow().shift(months=12).replace(hour=3, minute=00).isoformat()
    if period == "24 months":
        return utcnow().shift(months=24).replace(hour=3, minute=00).isoformat()
    if period == "48 months":
        return utcnow().shift(months=48).replace(hour=3, minute=00).isoformat()
    raise Exception("Period is not supported")


def get_intervals(
    min_date: str, max_date: str, unit: str, measure: float
) -> List[Tuple[str, str]]:
    """
    :param min_date: дата начала пириода
    :param max_date: дата окончания пириода
    :param unit: days, weeks,  fortnights, months
    :param measure: int шаг
    :return: List[Tuple[min_date, max_date]]
    """
    output = []
    while min_date < max_date:
        # записывет в перменную temp минимальную дату плюс (unit: measure)
        temp = get(min_date).shift(**{unit: measure}).isoformat()
        # записывает в output пару дат min_date и  меньшую дату min_date max_date или temp
        output.append((min_date, min(temp, max_date)))
        # меняет значение min_date на temp
        min_date = temp
    return output


def get_period(session: Session):
    """
    :param session:
    :return: {'since': str, 'until': str}
    """
    period_in = ["day", "week", "fortnight", "month"]
    if session.params["inputs"]["0"]["period"] not in period_in:
        return {
            "since": get(session.params["inputs"]["0"]["openDate"])
            .replace(day=1)
            .isoformat(),
            "until": get(session.params["inputs"]["0"]["openDate"])
            .ceil("month")
            .isoformat(),
        }
    if session.params["inputs"]["0"]["period"] == "day":
        return {
            "since": period_to_date(session.params["inputs"]["0"]["period"]),
            "until": utcnow().isoformat(),
        }

    else:
        return {
            "since": get(session.params["inputs"]["0"]["openDate"])
            .replace(hour=3, minute=00)
            .isoformat(),
            "until": get(session.params["inputs"]["0"]["closeDate"])
            .replace(hour=23, minute=00)
            .isoformat(),
        }


def get_period_day(session: Session):
    """
    :param session:
    :return: {'since': str, 'until': str}
    """
    if session.params["inputs"]["0"]["period"] == "day":
        return {
            "since": period_to_date(session.params["inputs"]["0"]["period"]),
            "until": get(period_to_date(session.params["inputs"]["0"]["period"]))
            .replace(hour=23, minute=00)
            .isoformat(),
        }

    else:
        return {
            "since": get(session.params["inputs"]["0"]["openDate"])
            .replace(hour=0, minute=1)
            .isoformat(),
            "until": get(session.params["inputs"]["0"]["openDate"])
            .replace(hour=23, minute=59)
            .isoformat(),
        }


# Получает список славарей
# Отдает xls
def json_to_xls_format_change(list: list):
    book = Workbook()

    # grab the active worksheet
    sheet = book.active
    sheet_row = ["A1", "B1", "C1", "D1", "E1", "F1", "G1", "H1", "J1", "K1", "L1", "M1"]
    columns_name = []
    for item in list:
        for k, v in item.items():
            if k not in columns_name:
                columns_name.append(k)

    columns = 0

    for name in columns_name:
        sheet[sheet_row[columns]] = name
        columns += 1

    row = 2
    for item in list:
        if len(item) > 0:
            last_column = 0
            for k, v in item.items():
                sheet[row][last_column].value = v
                last_column += 1
        row += 1
    return book


def xls_to_json_format_change(book):
    # Получаем активный лист из книги Excel
    ws = book.active

    my_list = []  # Создаем пустой список для хранения словарей

    # Находим номер последнего столбца и строки
    last_column = len(list(ws.columns))
    last_row = len(list(ws.rows))

    # Проходимся по каждой строке в таблице Excel
    for row in range(1, last_row + 1):
        my_dict = {}  # Создаем пустой словарь для текущей строки
        # Проходимся по каждому столбцу в текущей строке
        for column in range(1, last_column + 1):
            column_letter = get_column_letter(
                column
            )  # Получаем буквенное обозначение столбца
            if row > 1:  # Пропускаем первую строку, так как это заголовки
                # Добавляем элементы в словарь в формате "значение заголовка: значение ячейки"
                my_dict[ws[column_letter + str(1)].value] = ws[
                    column_letter + str(row)
                ].value
        if len(my_dict) > 0:  # Убеждаемся, что словарь не пустой
            my_list.append(my_dict)  # Добавляем словарь в список
    return my_list  # Возвращаем список словарей
