import PyPDF2
import time
import re
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from bd.model import Session
from arrow import utcnow, get
from typing import List, Tuple
from pprint import pprint


from openpyxl import Workbook
from openpyxl.utils import get_column_letter

# import psutil  # Для мониторинга загрузки процессора
from pprint import pprint


def format_message_list2(obj):
    text = ""  # Создаем пустую строку, в которую будем добавлять текст
    messages = []  # Создаем пустой список для хранения сообщений

    if len(obj) > 0:  # Проверяем, что входной объект не пуст
        for k, v in obj.items():  # Проходим по ключам и значениям в объекте
            key = str(k)  # Преобразуем ключ в строку
            val = str(v)  # Преобразуем значение в строку
            total_len = len(key) + len(val)  # Вычисляем общую длину ключа и значения
            pad = 31 - total_len % 31  # Вычисляем количество пробелов для выравнивания

            text += key  # Добавляем ключ в текст

            if pad > 0:
                text += " " * pad  # Добавляем пробелы для выравнивания

            if total_len > 31:
                text += " " * 2  # Добавляем двойные пробелы, если общая длина больше 31

            text += str(v)  # Добавляем значение в текст
            text += "\n"  # Добавляем символ новой строки

        # Разбиваем текст на части, если он слишком большой
        index = 0
        size = 4000
        while len(text) > 0:
            part = text[index : index + size]  # Вырезаем часть текста заданного размера
            index = part.rfind("\n")  # Находим последний символ новой строки в части
            if index == -1:
                index = len(
                    text
                )  # Если символ новой строки не найден, используем конец текста
            part = text[0:index]  # Выбираем часть текста до символа новой строки
            messages.append(
                "```\n" + part + "\n```"
            )  # Добавляем часть текста в список сообщений
            text = text[
                index:
            ].strip()  # Удаляем обработанную часть из текста и убираем пробелы

    return messages  # Возвращаем список сообщений


def format_message_list4(obj):
    text = ""  # Создаем пустую строку для хранения текста сообщений.
    messages = []  # Создаем пустой список для хранения отформатированных сообщений.

    if len(obj) > 0:  # Проверяем, есть ли объекты в списке.
        for i in obj:  # Проходим по каждому объекту в списке.
            for k, v in i.items():  # Проходим по каждой паре ключ-значение в объекте.
                key = str(k)  # Преобразуем ключ в строку.
                val = str(v)  # Преобразуем значение в строку.
                total_len = len(key) + len(
                    val
                )  # Вычисляем общую длину ключа и значения.
                pad = (
                    30 - total_len % 30
                )  # Вычисляем количество пробелов, чтобы выровнять текст.

                text += key  # Добавляем ключ к тексту.

                if pad > 0:  # Если нужно добавить пробелы для выравнивания,
                    text += " " * pad  # добавляем их.

                if total_len > 30:  # Если общая длина превышает 30 символов,
                    text += " " * 2  # добавляем 2 дополнительных пробела.

                text += str(v)  # Добавляем значение к тексту.
                text += "\n"  # Добавляем перевод строки между ключами и значениями.
            text += "\n"  # Добавляем пустую строку после каждого объекта.
            text += "******************************"  # Добавляем разделительную строку.
            text += "\n"

        text += ""  # Пустая строка (это выглядит как ошибка, потому что она ничего не делает).
        index = 0  # Начальный индекс для разделения текста на части.
        size = 4000  # Максимальная длина каждой части сообщения.
        while len(text) > 0:  # Пока есть текст для обработки:
            part = text[
                index : index + size
            ]  # Выбираем часть текста длиной не более 4000 символов.
            index = part.rfind(
                "\n"
            )  # Находим последний символ перевода строки в части.
            if index == -1:  # Если символ перевода строки не найден,
                index = len(text)  # используем всю часть текста.
            part = text[
                0:index
            ]  # Выбираем часть текста до найденного символа перевода строки.
            messages.append(
                "```\n" + part + "\n```"
            )  # Добавляем часть текста в список сообщений,
            text = text[index:].strip()  # и удаляем ее из исходного текста.

        return messages  # Возвращаем список отформатированных сообщений.


import PyPDF2
import time
import os
import re
import json
import requests
from pprint import pprint


def find_INN(resource, query, API_KEY):
    # Функция для поиска ИНН по запросу с использованием API Dadata
    BASE_URL = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/"
    url = BASE_URL + resource
    headers = {
        "Authorization": "Token " + API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    data = {"query": query}
    # Отправляем POST-запрос к API для поиска ИНН
    res = requests.post(url, data=json.dumps(data), headers=headers)
    # Возвращаем JSON-ответ
    return res.json()


def process_PDF_files(directory_path, API_KEY):
    # Функция для обработки PDF-файлов в указанной директории
    start_time = time.time()
    # Получаем список файлов в указанной директории
    pdfs = os.listdir(directory_path)
    results = []  # Здесь будем хранить результаты обработки
    dict_ = {}

    # Проходимся по всем файлам в директории
    for pdf_file_name in pdfs:
        # Проверяем, является ли файл PDF-файлом
        if ".pdf" in pdf_file_name.lower():
            # Открываем PDF-файл для чтения
            with open(os.path.join(directory_path, pdf_file_name), "rb") as pdf_file:
                # Создаем объект для чтения PDF
                read_pdf = PyPDF2.PdfReader(pdf_file)
                number_of_pages = len(read_pdf.pages)

                # Проходимся по всем страницам PDF-файла
                for i in range(number_of_pages):
                    page = read_pdf.pages[i]
                    page_content = page.extract_text()
                    page_content = page_content.split("\n")
                    name_ = ""
                    phone_ = ""
                    address_ = ""
                    inn_ = ""
                    сompany_ = ""
                    product_ = ""
                    address__ = False  # Флаг для обозначения начала сбора адреса

                    # Обработка текста на странице
                    for line in page_content:
                        # Проверяем, содержит ли строка информацию об ИНН
                        if re.search(r"^ИНН:", line):
                            inn_ = line.replace("ИНН: ", "").replace(".", "")
                            # Проверяем, был ли этот ИНН уже обработан ранее
                            if inn_[:-1] in dict_.keys():
                                сompany_ = dict_[inn_[:-1]]
                            else:
                                # Если ИНН новый, делаем запрос к API для получения информации о компании
                                name_company = find_INN("party", inn_[:-1], API_KEY)[
                                    "suggestions"
                                ][0]["value"]
                                # Сохраняем информацию о компании в словарь
                                dict_[inn_[:-1]] = name_company
                                сompany_ = dict_[inn_[:-1]]
                        # Проверяем, содержит ли строка информацию о ФИО
                        if re.search(r"^ФИО:", line):
                            name_ = line.replace("ФИО: ", "").replace(".", "")
                        # Проверяем, содержит ли строка информацию о телефоне
                        if re.search(r"^Телефон:", line):
                            phone_ = line.replace("Телефон: ", "")
                        # Обработка адреса
                        if address__:
                            # Собираем строку с адресом
                            address_ = (
                                address_
                                + " "
                                + line.replace("Адрес: ", "").replace(
                                    " ИНФОРМАЦИЯ ОБ ОТПРАВЛЕНИИ", ""
                                )
                            )
                            # Если достигнут конец блока адреса
                            if "ИНФОРМАЦИЯ ОБ ОТПРАВЛЕНИИ" in line:
                                address__ = False
                        # Начинаем сбор адреса
                        if re.search(r"^Адрес:", line) or re.search(r"^ПВЗ:", line):
                            if not "ИНФОРМАЦИЯ ОБ ОТПРАВЛЕНИИ" in line:
                                address__ = True
                            address_ = (
                                line.replace("Адрес: ", "")
                                .replace(" ПВЗ: ", "")
                                .replace(" ИНФОРМАЦИЯ ОБ ОТПРАВЛЕНИИ", "")
                            )
                        # Проверяем, содержит ли строка информацию о продукте
                        if "Арт." in line:
                            info_ = line.split(" ")
                            if len(info_) > 2:
                                if len(info_[2]) > 1:
                                    product_ = info_[2]
                                else:
                                    info_2 = (
                                        line.replace(")", "__")
                                        .replace("(", "__")
                                        .split("__")
                                    )
                                    product_ = info_2[2]

                    # Создаем словарь с полученной информацией и добавляем его в список результатов
                    result_entry = {
                        "ФИО": name_,
                        "Телефон": phone_,
                        "Адрес": address_,
                        "Продукт": product_,
                        "ИНН": inn_,
                        "Компания": сompany_,
                    }

                    # Добавляем результат обработки текущей страницы в общий список результатов
                    results.append(result_entry)
    end_time = time.time()
    execution_time = end_time - start_time
    pprint(f"Время выполнения функции process_PDF_files: {execution_time:.2f} секунд")
    return results


# Пример использования функции
API_KEY = "e847ba51dfe5006957aca33cbd3e158f234b2bfe"
# directory_path = "pdf"
