import logging
import json
import os
from datetime import datetime
from pathlib import Path

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from dotenv import load_dotenv

# Путь к файлу логов
LOG_FILE_PATH = Path("user_logs.jsonl")  # .jsonl — один JSON-объект на строку


def log_user_data(user: types.User, chat: types.Chat, message: types.Message) -> None:
    """
    Логирует данные пользователя в файл в формате JSONL (JSON Lines).
    """
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "user": {
            "id": getattr(user, "id", None),
            "is_bot": getattr(user, "is_bot", None),
            "first_name": getattr(user, "first_name", None),
            "last_name": getattr(user, "last_name", None),
            "username": getattr(user, "username", None),
            "language_code": getattr(user, "language_code", None),
            "is_premium": getattr(user, "is_premium", None),
            "added_to_attachment_menu": getattr(user, "added_to_attachment_menu", None),
        },
        "chat": {
            "id": getattr(chat, "id", None),
            "type": getattr(chat, "type", None),
            "title": getattr(chat, "title", None),
            "username": getattr(chat, "username", None),
        },
        "message_id": getattr(message, "message_id", None),
        "text": getattr(message, "text", None) or getattr(message, "caption", None) or "",
    }

    with LOG_FILE_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False, separators=(",", ":")) + "\n")


def create_dispatcher() -> Dispatcher:
    load_dotenv()

    token = os.getenv("CHAT_COM_TOKEN")
    if not token:
        raise RuntimeError("CHAT_COM_TOKEN is not set in .env")

    bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
    dispatcher = Dispatcher(bot)
    dispatcher.middleware.setup(LoggingMiddleware())

    @dispatcher.message_handler(commands=["start"])
    async def handle_start_command(message: types.Message) -> None:
        user = message.from_user
        user_id = user.id if user else "unknown"

        # Логируем данные пользователя
        if user:
            log_user_data(user, message.chat, message)

        # Отправляем сообщение с кнопкой копирования
        await message.bot.request(
            "sendMessage",
            data={
                "chat_id": message.chat.id,
                "text": f"Ваш telegram ID: {user_id}",
                "reply_markup": json.dumps(
                    {
                        "inline_keyboard": [
                            [
                                {
                                    "text": "Скопировать ID",
                                    "copy_text": {"text": str(user_id)},
                                }
                            ]
                        ]
                    }
                ),
            },
        )

    # Дополнительный обработчик: логировать все входящие сообщения (не только /start)
    @dispatcher.message_handler()
    async def log_all_messages(message: types.Message) -> None:
        user = message.from_user
        if user:
            log_user_data(user, message.chat, message)
        # Можно ничего не отвечать, или отправить echo:
        # await message.answer("Сообщение получено.")

    return dispatcher


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    dp = create_dispatcher()
    executor.start_polling(dp, skip_updates=True)


if __name__ == "__main__":
    main()
