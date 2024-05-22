from telegram import Telegram
from config import TELEGRAM_TOKEN_2
from bd.model import get_session, create_massage, Session
from state_machine import handle_message

import logging

logger = logging.getLogger(__name__)


async def handler(params, bot):
    try:
        logger.info("Начало обработки сообщения")

        # Создание сообщения
        message = create_massage(params)
        logger.debug(f"Созданное сообщение: {message}")

        # Получение сессии пользователя
        session = get_session(message.user_id)
        logger.debug(f"Полученная сессия: {session}")

        session.message = message
        # session.employee = find_employee(message.user_id)

        # Обработка сообщения
        await handle_message(bot, message, session)
        logger.info("Сообщение обработано успешно")
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}", exc_info=True)


if __name__ == "__main__":
    logger.info("Запуск бота")
    try:
        bot = Telegram(TELEGRAM_TOKEN_2, handler)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}", exc_info=True)
