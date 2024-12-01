from typing import Callable
from enum import Enum
import telebot
from telebot import types
from arrow import utcnow

from pprint import pprint
import mimetypes
import os
import sys  # Импортируем модуль sys для получения информации о текущем исключении
import asyncio
import time
import io


from bd.model import Message, Session, PDFFile
from reports import reports, get_reports
from util_s import (
    format_message_list5,
    format_message_list4,
    xls_to_json_format_change,
    process_PDF_files,
    process_PDF_files_rar,
    process_pdf_files,
    process_pdf_file_no_zip
)

import logging


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


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
    if message.text == "/log":
        text_file_path = "bot.log"
        with open(text_file_path, "rb") as text_file:
            await bot.send_document(490899906, document=text_file)

    next = lambda: handle_message(bot, message, session)
    try:
        await states[session.state](bot, message, session, next)
    except Exception as e:
        # print(ex)
        # raise ex
        logger.exception("Error handling message")
        logger.error(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")
        await bot.send_message(
            message.chat_id, f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}"
        )
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
    logger.debug(f"Handled init state for chat {message.chat_id}")

    # session.save()


async def handle_menu_state(
    bot: telebot.TeleBot, message: Message, session: Session, next: Callable
):
    session.params["report"] = message.text
    session.state = State.INPUT
    session.update(state=session.state, params=session.params)
    logger.debug(f"Handled init state for chat {message.chat_id}")
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

            logger.debug(f"Handled init state for chat {message.chat_id}")

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

            # Получаем имя файла
            file_name = os.path.basename(file_info.file_path)
            print("File name:", file_name)

            # Проверяем расширение файла
            file_extension = os.path.splitext(file_name)[1]
            print("File extension:", file_extension)

            if not file_extension:
                file_extension = mimetypes.guess_extension(mime_type)

            type_xls = [
                "application/vnd.ms-excel",
                "application/x-msexcel",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/x-msexcel",
            ]
            #  Проверяем тип MIME файла
            if file_extension in [".xls", ".xlsx"]:
                print("xls")

                src_list = xls_to_json_format_change(downloaded_file)

            elif mime_type == "application/zip":
                src_list = process_pdf_file(downloaded_file)

            elif mime_type == "application/pdf":
                src_list = process_pdf_file_no_zip(downloaded_file)

            else:
                src_list = process_PDF_files_rar(downloaded_file)
            # Сохраняем информацию о файле в сессии
            session.params["inputs"][str(room)][input_name] = src_list

        except Exception as e:
            logger.exception("Error sending messages")
            logger.error(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")
            await bot.send_message(message.chat_id, f"Error sending messages: {e}")

    session.state = State.INPUT
    session.update(params=session.params, state=session.state)
    logger.debug(f"Handled init state for chat {message.chat_id}")
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
    elif report.mime == "file_5":
        messages = format_message_list5(result[0])
        try:
            for m in messages:
                await bot.send_message(message.chat_id, m, parse_mode="MarkdownV2")
                await asyncio.sleep(0.1)

        except Exception as e:
            logger.exception("Error sending messages")
            logger.error(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")
            await bot.send_message(message.chat_id, f"Error sending messages: {e}")

        try:
            book_number = 1
            for book in result[1]:
                # await asyncio.sleep(0.5)
                book_name = "book_" + str(book_number) + ".xlsx"
                binary_book_he = io.BytesIO()
                book.save(binary_book_he)
                binary_book_he.seek(0)
                binary_book_he.name = (
                    book_name  # Устанавливаем имя файла в объекте BytesIO
                )
                await bot.send_document(message.chat_id, document=binary_book_he)
                book_number += 1

        except Exception as e:
            logger.exception("Error sending messages")
            logger.error(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")
            await bot.send_message(
                message.chat_id, f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}"
            )
    elif report.mime == "file":
        messages = format_message_list4(result[0])
        try:
            [
                await bot.send_message(message.chat_id, m, parse_mode="MarkdownV2")
                for m in messages
            ]

        except Exception as e:
            logger.exception("Error sending messages")
            logger.error(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")
            await bot.send_message(message.chat_id, f"Error sending messages: {e}")

        try:
            book_number = 1
            for book in result[1]:
                book_name = "book_" + str(book_number) + ".xlsx"

                binary_book_he = io.BytesIO()
                book.save(binary_book_he)
                binary_book_he.seek(0)
                binary_book_he.name = (
                    book_name  # Устанавливаем имя файла в объекте BytesIO
                )
                await bot.send_document(message.chat_id, document=binary_book_he)
                book_number += 1

        except Exception as e:
            logger.exception("Error sending messages")
            logger.error(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")
            await bot.send_message(message.chat_id, f"Error sending messages: {e}")

    elif report.mime == "file_7":
        messages = format_message_list4(result[0])
        try:
            [
                await bot.send_message(message.chat_id, m, parse_mode="MarkdownV2")
                for m in messages
            ]

        except Exception as e:
            logger.exception("Error sending messages")
            logger.error(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")
            await bot.send_message(message.chat_id, f"Error sending messages: {e}")

        try:
            book = result[1]
            book_name = "book.xlsx"

            binary_book_he = io.BytesIO()
            book.save(binary_book_he)
            binary_book_he.seek(0)
            binary_book_he.name = (
                book_name  # Устанавливаем имя файла в объекте BytesIO
            )
            await bot.send_document(message.chat_id, document=binary_book_he)

        except Exception as e:
            logger.exception("Error sending messages")
            logger.error(f"Ошибка: {e} на строке {sys.exc_info()[-1].tb_lineno}")
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
    logger.debug(f"Handled ready state for chat {message.chat_id}")

    # session.save()
    # await next()


states = {
    State.INIT: handle_init_state,
    State.MENU: handle_menu_state,
    State.INPUT: handle_input_state,
    State.REPLY: handle_reply_state,
    State.READY: handle_ready_state,
}
