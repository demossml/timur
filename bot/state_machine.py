from typing import Callable
from enum import Enum
import telebot
from telebot import types
from arrow import utcnow

from bd.model import Message, Session, PDFFile
from reports import reports, get_reports
from util import format_message_list4
import io
from pprint import pprint
import zipfile
import requests


import os
import re
import json
import requests
import PyPDF2
import traceback
import json
import re
import time
import rarfile


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


def process_PDF_files(downloaded_zip_file):
    API_KEY = "e847ba51dfe5006957aca33cbd3e158f234b2bfe"
    try:
        with zipfile.ZipFile(io.BytesIO(downloaded_zip_file), "r") as zip_ref:
            results = []  # Здесь будем хранить результаты обработки
            dict_ = {}
            for file_name in zip_ref.namelist():
                if file_name.lower().endswith(".pdf"):
                    pdf_content = zip_ref.read(file_name)
                    pdf_file = io.BytesIO(pdf_content)
                    try:
                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                        for page_num in range(len(pdf_reader.pages)):
                            page = pdf_reader.pages[page_num]
                            page_content = page.extract_text()
                            page_content = page_content.split("\n")
                            name_ = ""
                            phone_ = ""
                            address_ = ""
                            inn_ = ""
                            сompany_ = ""
                            product_ = ""
                            address__ = (
                                False  # Флаг для обозначения начала сбора адреса
                            )

                            for line in page_content:
                                if re.search(r"^ИНН:", line):
                                    inn_ = line.replace("ИНН: ", "").replace(".", "")
                                    if inn_[:-1] in dict_.keys():
                                        сompany_ = dict_[inn_[:-1]]
                                    else:
                                        name_company = find_INN(
                                            "party", inn_[:-1], API_KEY
                                        )["suggestions"][0]["value"]
                                        dict_[inn_[:-1]] = name_company
                                        сompany_ = dict_[inn_[:-1]]
                                if re.search(r"^ФИО:", line):
                                    name_ = line.replace("ФИО: ", "").replace(".", "")
                                if re.search(r"^Телефон:", line):
                                    if phone_ == "":
                                        phone_ = line.replace("Телефон: ", "")
                                if address__:
                                    address_ = (
                                        address_
                                        + " "
                                        + line.replace("Адрес: ", "")
                                        .replace(" ИНФОРМАЦИЯ ОБ ОТПРАВЛЕНИИ", "")
                                        .replace("ИНФОРМАЦИЯ ОБ ОТПРАВЛЕНИИ", "")
                                    )
                                    if "ИНФОРМАЦИЯ ОБ ОТПРАВЛЕНИИ" in line:
                                        address__ = False
                                if re.search(r"^Адрес:", line) or re.search(
                                    r"^ПВЗ:", line
                                ):
                                    if not "ИНФОРМАЦИЯ ОБ ОТПРАВЛЕНИИ" in line:
                                        address__ = True
                                    address_ = (
                                        line.replace("Адрес: ", "")
                                        .replace(" ПВЗ: ", "")
                                        .replace("ПВЗ: ", "")
                                        .replace(" ИНФОРМАЦИЯ ОБ ОТПРАВЛЕНИИ", "")
                                        .replace("ИНФОРМАЦИЯ ОБ ОТПРАВЛЕНИИ", "")
                                    )
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

                            result_entry = {
                                "ФИО": name_.strip(),
                                "Телефон": phone_.strip(),
                                "Адрес": address_.strip(),
                                "Продукт": product_.strip(),
                                "ИНН": inn_.strip(),
                                "Компания": сompany_.strip(),
                            }

                            results.append(result_entry)
                    except Exception as e:
                        print(f"Ошибка при чтении PDF-файла: {file_name}")
                        traceback.print_exc()

        # Преобразование результатов в формат JSON
        # json_results = json.dumps(results, ensure_ascii=False, indent=4)
        return results

    except zipfile.BadZipFile:
        print("Ошибка: Неверный zip-файл.")
        traceback.print_exc()
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        traceback.print_exc()


def process_PDF_files_rar(downloaded_rar_file):
    pprint("process_PDF_files_rar")
    API_KEY = "e847ba51dfe5006957aca33cbd3e158f234b2bfe"
    try:
        with rarfile.RarFile(io.BytesIO(downloaded_rar_file), "r") as rar_ref:
            results = []  # Здесь будем хранить результаты обработки
            dict_ = {}
            pprint(rar_ref)
            for file_name in rar_ref.namelist():
                if file_name.lower().endswith(".pdf"):
                    pdf_content = rar_ref.read(file_name)
                    pdf_file = io.BytesIO(pdf_content)
                    try:
                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                        for page_num in range(len(pdf_reader.pages)):
                            page = pdf_reader.pages[page_num]
                            page_content = page.extract_text()
                            page_content = page_content.split("\n")
                            name_ = ""
                            phone_ = ""
                            address_ = ""
                            inn_ = ""
                            сompany_ = ""
                            product_ = ""
                            address__ = (
                                False  # Флаг для обозначения начала сбора адреса
                            )

                            for line in page_content:
                                if re.search(r"^ИНН:", line):
                                    inn_ = line.replace("ИНН: ", "").replace(".", "")
                                    if inn_[:-1] in dict_.keys():
                                        сompany_ = dict_[inn_[:-1]]
                                    else:
                                        name_company = find_INN(
                                            "party", inn_[:-1], API_KEY
                                        )["suggestions"][0]["value"]
                                        dict_[inn_[:-1]] = name_company
                                        сompany_ = dict_[inn_[:-1]]
                                if re.search(r"^ФИО:", line):
                                    name_ = line.replace("ФИО: ", "").replace(".", "")
                                if re.search(r"^Телефон:", line):
                                    if phone_ == "":
                                        phone_ = line.replace("Телефон: ", "")
                                if address__:
                                    address_ = (
                                        address_
                                        + " "
                                        + line.replace("Адрес: ", "")
                                        .replace(" ИНФОРМАЦИЯ ОБ ОТПРАВЛЕНИИ", "")
                                        .replace("ИНФОРМАЦИЯ ОБ ОТПРАВЛЕНИИ", "")
                                    )
                                    if "ИНФОРМАЦИЯ ОБ ОТПРАВЛЕНИИ" in line:
                                        address__ = False
                                if re.search(r"^Адрес:", line) or re.search(
                                    r"^ПВЗ:", line
                                ):
                                    if not "ИНФОРМАЦИЯ ОБ ОТПРАВЛЕНИИ" in line:
                                        address__ = True
                                    address_ = (
                                        line.replace("Адрес: ", "")
                                        .replace(" ПВЗ: ", "")
                                        .replace("ПВЗ: ", "")
                                        .replace(" ИНФОРМАЦИЯ ОБ ОТПРАВЛЕНИИ", "")
                                        .replace("ИНФОРМАЦИЯ ОБ ОТПРАВЛЕНИИ", "")
                                    )
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

                            result_entry = {
                                "ФИО": name_.strip(),
                                "Телефон": phone_.strip(),
                                "Адрес": address_.strip(),
                                "Продукт": product_.strip(),
                                "ИНН": inn_.strip(),
                                "Компания": сompany_.strip(),
                            }

                            results.append(result_entry)
                    except Exception as e:
                        print(f"Ошибка при чтении PDF-файла: {file_name}")
                        traceback.print_exc()

        # Преобразование результатов в формат JSON
        # json_results = json.dumps(results, ensure_ascii=False, indent=4)
        return results

    except rarfile.BadRarFile:
        print("Ошибка: Неверный rar-файл.")
        traceback.print_exc()
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        traceback.print_exc()


def process_PDF_files_(downloaded_zip_file):
    try:
        with zipfile.ZipFile(io.BytesIO(downloaded_zip_file), "r") as zip_ref:
            for file_name in zip_ref.namelist():
                if file_name.lower().endswith(".pdf"):
                    pdf_content = zip_ref.read(file_name)
                    pdf_file = io.BytesIO(pdf_content)
                    try:
                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                        text = ""
                        for page_num in range(len(pdf_reader.pages)):
                            page = pdf_reader.pages[page_num]
                            text += page.extract_text()
                    except Exception as e:
                        print(f"Ошибка при чтении PDF-файла: {file_name}")
                        traceback.print_exc()
        return text
    except zipfile.BadZipFile:
        print("Ошибка: Неверный zip-файл.")
        traceback.print_exc()
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        traceback.print_exc()


# стадии сесии
class State(str, Enum):
    INIT = "INIT"
    MENU = "MENU"
    INPUT = "INPUT"
    REPLY = "REPLY"
    READY = "READY"


#
async def handle_message(bot: telebot.TeleBot, message: Message, session: Session):
    start = ["Menu", "/start", "Меню"]
    if message.text in start:
        session.state = State.INIT
        session.room = "0"
        session.update(room=session.room, state=session.state)
    next = lambda: handle_message(bot, message, session)
    try:
        await states[session.state](bot, message, session, next)
    except Exception as ex:
        # print(ex)
        # raise ex
        await bot.send_message(message.chat_id, f"Произошла ошибка {ex}")
        session.state = State.INIT
        next()


async def handle_init_state(
    bot: telebot.TeleBot, message: Message, session: Session, next: Callable
):

    start_menu = types.InlineKeyboardMarkup(row_width=2)
    for name, report in get_reports(session).items():
        button = types.InlineKeyboardButton(report.name, callback_data=name)
        start_menu.add(button)
    # await bot.delete_message(message.chat_id, message.message_id)
    await bot.send_message(message.chat_id, "Привет", reply_markup=start_menu)
    room = session.room
    session.params = {"inputs": {room: {}}}

    session.state = State.MENU
    session.update(params=session.params, state=session.state)

    # session.save()


async def handle_menu_state(
    bot: telebot.TeleBot, message: Message, session: Session, next: Callable
):
    session.params["report"] = message.text
    session.state = State.INPUT
    session.update(state=session.state, params=session.params)
    # session.save()
    await next()


async def handle_input_state(bot, message, session, next):
    report = reports[session.params["report"]]
    # print(report.get_inputs(session).items())
    for name, Input in report.get_inputs(session).items():
        # print(name)
        room = session.room
        if name not in session.params["inputs"][room]:
            session.params["input"] = name
            session.update(params=session.params)
            input = Input()
            if input.type == "SELECT":
                markup = types.InlineKeyboardMarkup(row_width=2)
                options = input.get_options(session)  # [{}, {}, {}, ...]
                for option in options:  # [({}, 0), ({}, 1), ({}, 2)]
                    button = types.InlineKeyboardButton(
                        option["name"], callback_data=option["id"]
                    )
                    markup.add(button)
            if input.type == "LOCATION":
                options = input.get_options(session)  # [{}, {}, {}, ...]
                print(options[0]["name"])
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                btn_address = types.KeyboardButton(
                    options[0]["name"], request_location=True
                )
                markup.add(btn_address)
            if input.type == "PHOTO":
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                btn_address = types.KeyboardButton("Меню")
                markup.add(btn_address)
                await bot.send_message(message.chat_id, input.desc, reply_markup=markup)
            if input.type == "FILE":
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
                btn_address = types.KeyboardButton("Меню")
                markup.add(btn_address)
                await bot.send_message(message.chat_id, input.desc, reply_markup=markup)
            if input.type == "MESSAGE":
                await bot.delete_message(message.chat_id, message.message_id)
                await bot.send_message(message.chat_id, input.desc)
            if input.type == "SELECT":
                await bot.delete_message(message.chat_id, message.message_id)
                await bot.send_message(message.chat_id, input.desc, reply_markup=markup)
            if input.type == "LOCATION":
                await bot.delete_message(message.chat_id, message.message_id)
                await bot.send_message(message.chat_id, input.desc, reply_markup=markup)
            session.state = State.REPLY
            session.update(state=session.state)
            # session.save()

            return

    session.state = State.READY
    session.update(state=session.state)
    # session.save()
    await next()


async def handle_reply_state(bot, message, session, next):
    input_name = session.params["input"]
    room = session.room
    if message.text == "open":
        session.room = str(int(session.room) + 1)
        session.params["inputs"][session.room] = {}
        session.update(params=session.params, room=session.room)
    if str(room) not in session.params["inputs"]:
        session.params["inputs"][str(room)] = {}
        session.update(params=session.params)

    session.params["inputs"][str(room)][input_name] = message.text
    session.update(params=session.params)
    # session.params["inputs"][input_name] = message.text

    if message.location:
        session.params["inputs"][str(room)][input_name] = utcnow().now().isoformat()
        session.params["inputs"][str(room)][input_name] = {}
        session.params["inputs"][str(room)][input_name]["data"] = (
            utcnow().now().isoformat()
        )
        session.params["inputs"][str(room)][input_name][
            "lat"
        ] = message.location.latitude
        session.params["inputs"][str(room)][input_name][
            "lon"
        ] = message.location.longitude
        session.update(params=session.params)

    if message.photo:
        session.params["inputs"][str(room)][input_name] = {}
        session.params["inputs"][str(room)][input_name]["photo"] = message.photo[
            -1
        ].file_id
        session.update(params=session.params)

    if message.document:
        pprint(message.document.mime_type)

        try:
            mime_type = message.document.mime_type
            file_info = await bot.get_file(message.document.file_id)
            downloaded_file = await bot.download_file(file_info.file_path)

            if mime_type == "application/zip":
                src_list = process_PDF_files(downloaded_file)
            else:
                src_list = process_PDF_files_rar(downloaded_file)

            # Сохраняем информацию о файле в сессии
            session.params["inputs"][str(room)][input_name] = src_list

        except Exception as e:
            print(f"Произошла ошибка при обработке файла: {e}")
            await bot.send_message(message.chat_id, f"Error sending messages: {e}")

    session.state = State.INPUT
    session.update(params=session.params, state=session.state)
    # session.save()
    await next()


async def handle_ready_state(bot, message, session, next):
    report = reports[session.params["report"]]
    result = report.generate(session)
    # await bot.delete_message(message.chat_id, message.message_id)
    if report.mime == "image":
        if len(result[0]) > 0:
            for k, v in result[0].items():
                file_id = v
                await bot.send_photo(message.chat_id, file_id)
                messages = format_message_list4(result[1])
            [
                await bot.send_message(message.chat_id, m, parse_mode="MarkdownV2")
                for m in messages
            ]
        else:
            messages = format_message_list4(result[1])
            [
                await bot.send_message(message.chat_id, m, parse_mode="MarkdownV2")
                for m in messages
            ]
    if report.mime == "file":
        messages = format_message_list4(result[0])
        try:
            [
                await bot.send_message(message.chat_id, m, parse_mode="MarkdownV2")
                for m in messages
            ]
        except Exception as e:
            print(f"Error sending messages: {e}")
            await bot.send_message(message.chat_id, f"Error sending messages: {e}")

        try:
            book_he = result[1]
            # pprint(book_he)
            binary_book_he = io.BytesIO()
            book_he.save(binary_book_he)
            binary_book_he.seek(0)
            binary_book_he.name = (
                "book_he.xlsx"  # Устанавливаем имя файла в объекте BytesIO
            )
            await bot.send_document(message.chat_id, document=binary_book_he)

            book_she = result[2]
            binary_book_she = io.BytesIO()
            book_she.save(binary_book_she)
            binary_book_she.seek(0)
            binary_book_she.name = (
                "book_she.xlsx"  # Устанавливаем имя файла в объекте BytesIO
            )
            await bot.send_document(message.chat_id, document=binary_book_she)
        except Exception as e:
            print(f"Error sending document: {e}")
            await bot.send_message(message.chat_id, f"Error sending messages: {e}")

    else:
        messages = format_message_list4(result)
        [
            await bot.send_message(message.chat_id, m, parse_mode="MarkdownV2")
            for m in messages
        ]
    session.state = State.INIT
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_address = types.KeyboardButton("Меню")
    markup.add(btn_address)
    await bot.delete_message(message.chat_id, message.message_id)
    await bot.send_message(message.chat_id, "Привет", reply_markup=markup)
    session.update(state=session.state)
    # session.save()
    # await next()


states = {
    State.INIT: handle_init_state,
    State.MENU: handle_menu_state,
    State.INPUT: handle_input_state,
    State.REPLY: handle_reply_state,
    State.READY: handle_ready_state,
}
