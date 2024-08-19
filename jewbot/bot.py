import os
import sqlite3
import asyncio
import re
from io import BytesIO

from aiogram.types import FSInputFile

from database.db_manager import DataBase

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from telethon import TelegramClient, events
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart

# --- Telethon --- #
api_id = 25404839
api_hash = '63cdb13b5a70a129f301b84f1cd3b455'
client = TelegramClient('27749763255/27749763255.session', api_id, api_hash)

# --- Aiogram --- #
bot = Bot(token="7452829269:AAFslnBL0gLKJLrFA4CqWHcViqvjQxFc_kk")
dp = Dispatcher()

# --- SQLite --- #
db = DataBase()

# --- Settings --- #
TARGET_CHAT_ID = 418921990
CHANNEL_NAME = 'Записки еврея'


def keywords_in_string(keywords, string):
    search_string = string.lower()
    keywords = set(keyword.lower() for keyword in keywords)
    pattern = re.compile('|'.join(re.escape(keyword) for keyword in keywords))
    matches = pattern.findall(search_string)
    return bool(matches)


async def start_telethon():
    """
    Запускает Telethon клиента и обрабатывает сообщения из нужного канала.
    """
    await client.start()
    dialogs = await client.get_dialogs()
    target_dialog = None

    for dialog in dialogs:
        if dialog.title == CHANNEL_NAME:
            target_dialog = dialog
            break

    if not target_dialog:
        print("Канал не найден.")
        return

    # Обработчик новых сообщений
    @client.on(events.NewMessage(chats=target_dialog))
    async def handler(event):
        message_text = event.message.message
        print(f"Новый пост: {message_text}")

        for user_id, user_filter in db.get_users():
            if keywords_in_string(user_filter.split(), message_text):
                if event.message.media:
                    await event.message.download_media('temp.jpg')
                    await bot.send_photo(chat_id=user_id, photo=FSInputFile('temp.jpg'), caption=message_text)
                    os.remove('temp.jpg')
                else:
                    await bot.send_message(chat_id=user_id, text=message_text)

    print("# Бот запущен.\n# Парсер запущен.")
    await client.run_until_disconnected()


async def start_aiogram():
    """
    Запускает Aiogram бота и его диспетчер.
    """

    async def send_welcome(message: types.Message):
        await message.answer("Привет! Это бот на Aiogram.")

    dp.message.register(send_welcome, CommandStart())

    await dp.start_polling(bot)


class Form(StatesGroup):
    user_filter = State()


@dp.message(Command("filter"))
async def start_command(message: types.Message, state: FSMContext):
    await message.answer("Введите свой фильтр:")
    await state.set_state(Form.user_filter)


@dp.message(Form.user_filter)
async def process_name(message: types.Message, state: FSMContext):
    new_user_filter = message.text[0:35]
    db.add_user(message.chat.id, new_user_filter)
    await message.answer(f'Задан новый фильтр: "{new_user_filter}"')
    await state.clear()


async def main():
    """
    Запускает оба сервиса (Telethon и Aiogram) параллельно.
    """
    await asyncio.gather(start_telethon(), start_aiogram())


if __name__ == "__main__":
    asyncio.run(main())
