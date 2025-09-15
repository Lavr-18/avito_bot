import os
import time
import openai
from dotenv import load_dotenv

# Импортируем все необходимые константы из вашего файла
from constants import (
    BOT_GREETING_MESSAGE,
    BOT_GREETING_MESSAGE_UNWORKING_HOURS,
    BOT_CANT_ANSWER_MESSAGE,
    RESPONSES,
    INTENT_GREETINGS,
    INTENT_OTHER
)

load_dotenv()

# Установка API-ключа OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if OPENAI_API_KEY:
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
else:
    print("Ошибка: OPENAI_API_KEY не найден. Установите переменную окружения или добавьте ключ в код.")
    exit()


def get_intent_and_response(user_message):
    """
    Анализирует намерение пользователя с помощью OpenAI API
    и возвращает соответствующий шаблон ответа.
    """
    print('Анализ намерения пользователя...')
    try:
        # Убираем INTENT_GREETINGS и INTENT_OTHER из списка для анализа, т.к. они обрабатываются отдельно
        intents_for_prompt = ", ".join(
            [intent for intent in RESPONSES.keys() if intent not in [INTENT_GREETINGS, INTENT_OTHER]]
        )
        prompt = (
            f"Являясь помощником, оцени следующее сообщение пользователя: '{user_message}'. "
            f"Определи основное намерение из списка: {intents_for_prompt}, {INTENT_GREETINGS}, {INTENT_OTHER}. "
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
        print(f'Определено намерение: {intent}')

        if intent == INTENT_GREETINGS:
            # Возвращаем приветственное сообщение, но т.к. оно отправляется первым,
            # здесь можно вернуть что-то другое или null
            return None  # Здесь мы не будем отправлять второе приветствие.

        if intent in RESPONSES:
            return RESPONSES[intent]
        else:
            return BOT_CANT_ANSWER_MESSAGE

    except openai.APIError as e:
        print(f'Ошибка OpenAI API: {e}')
        return "Произошла ошибка при обращении к боту. Попробуйте еще раз."
    except Exception as e:
        print(f'Непредвиденная ошибка при работе с OpenAI: {e}')
        return "Произошла ошибка при обращении к боту. Попробуйте еще раз."


def main():
    print("Запуск тестового бота. Для выхода введите 'выход'.")
    print("-" * 30)

    # Имитация рабочего времени
    is_working_hours = input("Сейчас рабочее время? (да/нет): ").lower().strip() == 'да'

    while True:
        user_input = input("Сообщение от пользователя: ")
        if user_input.lower() == 'выход':
            break

        # Этап 1: Отправка приветствия
        greeting_message = BOT_GREETING_MESSAGE if is_working_hours else BOT_GREETING_MESSAGE_UNWORKING_HOURS
        print(f"Ответ бота (1/2): {greeting_message}")

        time.sleep(1)  # Имитация задержки, как в основном скрипте

        # Этап 2: Анализ намерения и отправка второго ответа
        bot_response = get_intent_and_response(user_input)
        if bot_response:
            print(f"Ответ бота (2/2): {bot_response}")
        else:
            print("Ответ бота (2/2): <Ответ не требуется>")

        print("-" * 30)


if __name__ == "__main__":
    main()