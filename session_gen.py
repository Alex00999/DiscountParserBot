import os
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError

# Загружаем переменные окружения
load_dotenv()

# Получаем API ID, API HASH и номер телефона из .env файла
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
phone = os.getenv("PHONE")

# Проверяем наличие необходимых переменных
if not api_id or not api_hash or not phone:
    print("Ошибка: Убедитесь, что API_ID, API_HASH и PHONE указаны в .env файле.")
    exit(1)

# Преобразуем API ID в целое число
try:
    api_id = int(api_id)
except ValueError:
    print("Ошибка: API_ID должен быть целым числом.")
    exit(1)

# Название файла сессии
session_file = 'telethon_parser.session'

# Создаем клиента
with TelegramClient(session_file, api_id, api_hash) as client:
    try:
        # Проверяем, авторизован ли клиент
        if not client.is_user_authorized():
            # Принудительно запрашиваем код через приложение Telegram
            client.send_code_request(phone, force_sms=False)
            print("Введите код, отправленный в приложение Telegram:")

            while True:
                code = input("Код: ")
                try:
                    client.sign_in(phone, code)
                    break
                except PhoneCodeInvalidError:
                    print("Ошибка: Неверный код. Попробуйте снова.")

            # Проверка двухфакторной аутентификации
            if client.is_user_authorized():
                try:
                    me = client.get_me()
                    print(f"Успешная авторизация! Вы вошли как {me.username}")
                except SessionPasswordNeededError:
                    password = input("Введите пароль двухфакторной аутентификации: ")
                    client.sign_in(password=password)

        else:
            print("Вы уже авторизованы.")

        # Сохранение StringSession
        print("Сессия успешно создана и сохранена в файле 'telethon_parser.session'.")
        print("StringSession:", StringSession.save(client.session))

    except Exception as e:
        print(f"Произошла ошибка: {e}")
