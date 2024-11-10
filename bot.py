import asyncio
import re

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton

from database import DataBase

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from telethon import TelegramClient, events
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart

from dotenv import load_dotenv
import os

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
print(api_id, api_hash)
client = TelegramClient('telethon_parser.session', api_id, api_hash)

bot = Bot(token=os.getenv("AIOGRAM_BOT_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()
db = DataBase()


def keywords_in_string(keywords, string):
    search_string = string.lower()
    keywords = set(keyword.lower() for keyword in keywords)
    pattern = re.compile('|'.join(re.escape(keyword) for keyword in keywords))
    matches = pattern.findall(search_string)
    return bool(matches)


async def start_telethon():
    """
    Запускает Telethon клиента и обрабатывает сообщения из всех каналов.
    """
    await client.start()

    # Обработчик новых сообщений
    @client.on(events.NewMessage())
    async def handler(event):
        # Получаем название чата
        chat_title = ''
        if event.chat and hasattr(event.chat, 'title'):
            chat_title = event.chat.title

        # Проверяем, является ли название чата "Telegram"
        if chat_title == 'Telegram':
            return  # Игнорируем сообщения из этого чата

        if event.message.peer_id and hasattr(event.message.peer_id, 'channel_id'):
            channel_id = event.message.peer_id.channel_id
            message_id = event.message.id
            message_text = event.message.message
            formatted_message_text = message_text + f'\n\n<b>Ссылка на пост:</b> https://t.me/c/{channel_id}/{message_id}'
            print(f"Новый пост: {message_text}")
            print(db.get_users())
            for user_id, user_filter in db.get_users():
                print(keywords_in_string(user_filter.split(), message_text))
                if keywords_in_string(user_filter.split(), message_text):
                    if event.message.media:
                        try:
                            await event.message.download_media('temp.jpg')
                            await bot.send_photo(chat_id=user_id, photo=FSInputFile('temp.jpg'),
                                                 caption=formatted_message_text)
                            os.remove('temp.jpg')
                        except:
                            await bot.send_message(chat_id=user_id, text=formatted_message_text)
                    else:
                        await bot.send_message(chat_id=user_id, text=formatted_message_text)

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
