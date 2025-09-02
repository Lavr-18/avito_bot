import json
import logging
import os
import time
from datetime import datetime

import openai
import pytz
import requests
import yaml
from dotenv import load_dotenv

from config import configure_logging
from constants import (
    BOT_GREETING_MESSAGE,
    BOT_GREETING_MESSAGE_UNWORKING_HOURS,
    BOT_CANT_ANSWER_MESSAGE,
    GET_CHAT_MESSAGES_URL,
    MESSEGE_URL,
    SEND_URL,
    TIME_ZONE,
    RESPONSES,
    INTENT_GREETINGS,
    INTENT_OTHER
)
from refresh_token import refresh_token

load_dotenv()

USER_ID = os.getenv("USER_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if OPENAI_API_KEY:
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
else:
    logging.error("OPENAI_API_KEY не найден в переменных окружения. Убедитесь, что он добавлен в файл .env.")
    exit()


def get_headers():
    """
    Функция получает сохраненный в файле token.yml токен
    и возвращает headers, необходимые для отправки запросов.
    """
    logging.info('get_headers: Начало получения заголовков.')
    try:
        with open("token.yml") as file:
            token = yaml.safe_load(file)["token"]
        headers = {
            "Content_Type": "application/json",
            "Authorization": f"Bearer {token}"}
        logging.info('get_headers: Заголовки успешно получены.')
        return headers
    except Exception as e:
        logging.error(f'Ошибка при работе функции get_headers - {e}')
        if "No such file or directory" in str(e):
            logging.info('Файл token.yml не найден. Запускаем обновление токена.')
            refresh_token()
            return get_headers()
        return None


def get_all_chats(headers):
    """
    Функция отправляет запрос на получение всех чатов.
    """
    logging.info('get_all_chats: Начало запроса всех чатов.')
    try:
        chats = requests.get(
            MESSEGE_URL.format(USER_ID=USER_ID),
            headers=headers)
        logging.info(f'get_all_chats: Ответ от API. Статус-код: {chats.status_code}')
        chats_data = json.loads(chats.text)
        logging.debug(f'get_all_chats: Получены данные чатов: {chats_data}')
        return chats_data
    except (ConnectionError,
            TimeoutError,
            requests.exceptions.ConnectionError) as e:
        logging.error(f'Ошибка соединения при работе get_all_chats: {e}')
        return None
    except Exception as e:
        logging.error(f'Новая ошибка при работе функции get_all_chats - {e}')
        return None


def get_intent_and_response(user_message):
    """
    Анализирует намерение пользователя с помощью OpenAI API
    и возвращает соответствующий шаблон ответа.
    """
    logging.info('get_intent_and_response: Анализ намерения пользователя.')
    try:
        intents_list = ", ".join(RESPONSES.keys())
        prompt = (
            f"Являясь помощником, оцени следующее сообщение пользователя: '{user_message}'. "
            f"Определи основное намерение из списка: {intents_list}, {INTENT_GREETINGS}, {INTENT_OTHER}. "
            f"Выведи только одно ключевое слово, соответствующее намерению, без объяснений. "
            f"Например: ВИЗИТ."
        )

        response = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=20,
            n=1,
            stop=None,
            temperature=0.5
        )

        intent = response.choices[0].text.strip().upper()
        logging.info(f'get_intent_and_response: Определено намерение: {intent}')

        if intent in RESPONSES:
            return RESPONSES[intent]
        else:
            return None

    except openai.OpenAIError as e:
        logging.error(f'Ошибка OpenAI API: {e}')
        return None
    except Exception as e:
        logging.error(f'Непредвиденная ошибка при работе с OpenAI: {e}')
        return None


def send_message(chat_id, headers, text):
    """
    Функция отправляет сообщение с указанным текстом.
    """
    logging.info(f'send_message: Начало отправки сообщения в чат {chat_id}.')
    try:
        data = {
            "message": {
                "text": text},
            "type": "text"}
        chats = requests.post(
            url=SEND_URL.format(USER_ID=USER_ID, chat_id=chat_id),
            headers=headers,
            data=json.dumps(data))
        logging.info(f'Сообщение отправлено! Текст: "{text}", Чат ID: {chat_id}. Статус: {chats.status_code}')
    except Exception as e:
        logging.error(f'Ошибка при работе функции send_message - {e}')


def get_chat_messages(chat_id, headers):
    """
    Функция получает все сообщения в конкретном чате (chat_id).
    """
    logging.info(f'get_chat_messages: Начало проверки сообщений в чате {chat_id}.')
    try:
        chats = requests.get(
            url=GET_CHAT_MESSAGES_URL.format(USER_ID=USER_ID, chat_id=chat_id),
            headers=headers)
        logging.info(f'get_chat_messages: Статус-код ответа: {chats.status_code}')
        messages_data = json.loads(chats.text)
        logging.debug(f'get_chat_messages: Получены данные сообщений: {messages_data}')
        return messages_data
    except Exception as e:
        logging.error(f'Ошибка при работе функции get_chat_messages - {e}')
        return None


def check_chat(chat, headers):
    """
    Функция проверяет чат по следующим критериям:
    - Последнее сообщение было отправлено не ботом.
    - Сообщение было отправлено менее 180 секунд назад.
    - В чате не было исходящих сообщений более 3 часов.
    """
    logging.info('check_chat: Начало проверки чата.')
    author_id = chat["last_message"]["author_id"]
    if author_id == 0:
        logging.info('check_chat: Последнее сообщение от Avito, пропускаем.')
        return False

    chat_id = chat["id"]

    update_time_ago = int(time.time()) - chat["updated"]
    logging.info(f'check_chat: Сообщение в чате {chat_id} было обновлено {update_time_ago} секунд назад.')
    if update_time_ago > 180:
        logging.info(f'check_chat: Сообщение в чате {chat_id} старше 180 секунд. Игнорируем.')
        return False

    messages = get_chat_messages(chat_id, headers=headers)
    if not messages or "messages" not in messages:
        logging.warning('check_chat: Не удалось получить сообщения чата. Пропускаем.')
        return False

    last_message = messages["messages"][0]

    if last_message["direction"] == "out":
        logging.info(f'check_chat: Последнее сообщение в чате {chat_id} отправлено ботом. Игнорируем.')
        return False

    last_outgoing_time = None
    for message in messages["messages"]:
        if message["direction"] == "out":
            last_outgoing_time = message["created"]
            break

    current_time_ago = int(time.time())
    if last_outgoing_time and (current_time_ago - last_outgoing_time) < 10800:
        logging.info(f'check_chat: В чате {chat_id} уже была переписка с ботом менее 3 часов назад. Игнорируем.')
        return False

    logging.info(f'check_chat: Обнаружено новое сообщение, требующее ответа в чате {chat_id}.')
    logging.debug(f'check_chat: Текст последнего сообщения: {last_message["content"]["text"]}')
    return True


def check_upcoming_and_answer():
    logging.info('check_upcoming_and_answer: Запуск основной функции.')
    headers = get_headers()
    if not headers:
        logging.error('Не удалось получить заголовки, прекращаем работу.')
        return

    chats_response = get_all_chats(headers)

    if not chats_response:
        logging.error('Не удалось получить список чатов. Возможно, ошибка в API.')
        return

    try:
        chats = chats_response["chats"]
        if not chats:
            logging.info('Входящих сообщений нет. Проверяем все чаты вручную.')
    except KeyError as e:
        logging.error(f'KeyError {e} - Ответ от API не содержит ключа "chats". Возможно, токен недействителен.')
        refresh_token()
        logging.info('Токен обновлен. Повторный запуск.')
        headers = get_headers()
        chats_response = get_all_chats(headers)
        if chats_response and "chats" in chats_response:
            chats = chats_response["chats"]
        else:
            logging.error('Повторная попытка не удалась. Возможно, проблема с API или токеном.')
            return

    try:
        if len(chats) > 0:
            logging.info(f'Найдено {len(chats)} чат(ов) в ответе API.')
            for chat in chats:
                if check_chat(chat, headers):
                    chat_id = chat["id"]

                    # Проверяем, рабочее ли сейчас время
                    tz = pytz.timezone(TIME_ZONE)
                    now = datetime.now(tz)
                    current_time = now.time()
                    time_09_00 = datetime.strptime("09:00", "%H:%M").time()
                    time_20_00 = datetime.strptime("20:00", "%H:%M").time()

                    # Отправляем первое сообщение в зависимости от времени
                    if time_09_00 <= current_time <= time_20_00:
                        send_message(chat_id, headers, BOT_GREETING_MESSAGE)
                    else:
                        send_message(chat_id, headers, BOT_GREETING_MESSAGE_UNWORKING_HOURS)

                    time.sleep(2)  # Задержка для последовательной отправки

                    # Всегда отправляем второе сообщение с анализом намерения
                    messages = get_chat_messages(chat_id, headers=headers)
                    if messages and "messages" in messages:
                        user_message_text = messages["messages"][0]["content"]["text"]
                        bot_response = get_intent_and_response(user_message_text)
                        if bot_response:
                            send_message(chat_id, headers, bot_response)
        else:
            logging.info('Нет чатов, требующих внимания.')
    except Exception as e:
        logging.error(
            f'Ошибка при работе check_upcoming_and_answer - {e}')


last_token_refresh = 0


def main():
    configure_logging()
    global last_token_refresh

    while True:
        try:
            if time.time() - last_token_refresh > 43200:
                logging.info("Обновление токена. Прошло 12 часов.")
                refresh_token()
                last_token_refresh = time.time()

            check_upcoming_and_answer()
        except Exception as e:
            logging.error(f'Ошибка в основном цикле: {e}')

        time.sleep(20)


if __name__ == "__main__":
    main()
