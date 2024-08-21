import os
import asyncio
import re

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from database import DataBase

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from telethon import TelegramClient, events
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart

# --- Telethon --- #
api_id = 25404839
api_hash = '63cdb13b5a70a129f301b84f1cd3b455'
client = TelegramClient('sessions/27749763255.session', api_id, api_hash)

# --- Aiogram --- #
bot = Bot(token="7452829269:AAFslnBL0gLKJLrFA4CqWHcViqvjQxFc_kk",
          default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# --- SQLite --- #
db = DataBase()

# --- Settings --- #
CHANNEL_NAME = 'тест бота'


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
        if dialog.title.lower() == CHANNEL_NAME:
            target_dialog = dialog
            break

    if not target_dialog:
        print("Канал не найден.")
        return

    # Обработчик новых сообщений
    @client.on(events.NewMessage(chats=target_dialog))
    async def handler(event):
        channel_id = event.message.peer_id.channel_id
        message_id = event.message.id
        message_text = event.message.message
        print(f"Новый пост: {message_text}")

        for user_id, user_filter in db.get_users():
            if keywords_in_string(user_filter.split(), message_text):
                message_text = message_text + f'\n\n<b>Ссылка на пост:</b> https://t.me/c/{channel_id}/{message_id}'
                if event.message.media:
                    await event.message.download_media('temp.jpg')
                    await bot.send_photo(chat_id=user_id, photo=FSInputFile('temp.jpg'), caption=message_text)
                    os.remove('temp.jpg')
                else:
                    await bot.send_message(chat_id=user_id, text=message_text)

    print("# Парсер запущен.")
    await client.run_until_disconnected()


async def start_aiogram():
    """
    Запускает Aiogram бота и его диспетчер.
    """

    async def send_welcome(message: types.Message):
        await message.answer(
            "<b>Шалом! ✡️ \n \nЭто бот-фильтр для телеграм канала Записки Еврея."
            " Просто задай ключевые слова, по которым бот будет фильтровать посты и <u>включи уведомления</u>."
            "</b>\n \n/filter - настройки фильтра")

    dp.message.register(send_welcome, CommandStart())

    print("# Бот запущен.")
    await dp.start_polling(bot)


@dp.message(Command("filter"))
async def filter_command(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Изменить фильтр 📝', callback_data='change_filter_button')],
        [InlineKeyboardButton(text='Отписаться от рассылки 🚫', callback_data='unsubscribe_button')]
    ])
    current_filter = db.get_user_filter(message.from_user.id)
    if not current_filter:
        current_filter = 'не задан'
    await message.answer(text='<b>Текущий фильтр:</b> ' + current_filter,
                         reply_markup=keyboard)


class Form(StatesGroup):
    user_filter = State()


@dp.callback_query(lambda c: c.data == 'change_filter_button')
async def process_callback_button_click(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(
        chat_id=callback_query.from_user.id,
        text="<b>Введите новый фильтр, пишите ключевые слова через пробел.\nОграничение 150 символов.\nПример:</b> 4070 чайник видеокарта пылесос\n",
    )
    await state.set_state(Form.user_filter.state)
    await callback_query.answer()


@dp.callback_query(lambda c: c.data == 'unsubscribe_button')
async def process_unsubscribe_button_click(callback_query: types.CallbackQuery):
    await bot.send_message(
        chat_id=callback_query.from_user.id,
        text="Вы отписались от рассылки! 🙁",
    )
    db.add_user(callback_query.from_user.id, '')
    await callback_query.answer()


@dp.message(Form.user_filter)
async def process_name(message: types.Message, state: FSMContext):
    new_user_filter = message.text[0:150]
    db.add_user(message.chat.id, new_user_filter)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Изменить фильтр 📝', callback_data='change_filter_button')],
        [InlineKeyboardButton(text='Отписаться от рассылки 🚫', callback_data='unsubscribe_button')]
    ])
    await message.answer(
        text='<b>Текущий фильтр:</b> ' + new_user_filter,
        reply_markup=keyboard
    )
    await state.clear()


async def main():
    """
    Запускает оба сервиса (Telethon и Aiogram) параллельно.
    """
    await asyncio.gather(start_telethon(), start_aiogram())


if __name__ == '__main__':
    asyncio.run(main())
