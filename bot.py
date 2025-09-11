import logging
import json
import os

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from dotenv import load_dotenv


def create_dispatcher() -> Dispatcher:
    load_dotenv()

    token = os.getenv("CHAT_COM_TOKEN")
    if not token:
        raise RuntimeError("CHAT_COM_TOKEN is not set in .env")

    bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
    dispatcher = Dispatcher(bot)
    dispatcher.middleware.setup(LoggingMiddleware())

    @dispatcher.message_handler(commands=["start"])  # type: ignore[misc]
    async def handle_start_command(message: types.Message) -> None:
        user_id = message.from_user.id if message.from_user else "unknown"

        # Use low-level API call to send an inline button with copy-to-clipboard support
        # via Bot API's `copy_text` field (works in Telegram apps that support it).
        await message.bot.request(
            "sendMessage",
            data={
                "chat_id": message.chat.id,
                "text": f"Ваш telegramm ID: {user_id}",
                # Bot API expects reply_markup as a JSON-serialized string when sent raw
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


