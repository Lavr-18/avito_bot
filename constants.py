from pathlib import Path

BASE_DIR = Path(__file__).parent

# LOGGING
LOG_DIR = 'logs'
LOG_FILE = 'avito.log'
TIME_ZONE = 'Europe/Moscow'
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'

GRANT_TYPE = 'client_credentials'

# URLS
TOKEN_URL = 'https://api.avito.ru/token'
BASE_URL = "https://api.avito.ru/messenger/"
MESSEGE_URL = "https://api.avito.ru/messenger/v2/accounts/{USER_ID}/chats"
READ_URL = "https://api.avito.ru/messenger/v1/accounts/{USER_ID}/chats/{chat_id}/read"
SEND_URL = "https://api.avito.ru/messenger/v1/accounts/{USER_ID}/chats/{chat_id}/messages"
GET_CHAT_MESSAGES_URL = "https://api.avito.ru/messenger/v3/accounts/{USER_ID}/chats/{chat_id}/messages/"

# Время в секундах
THREE_HOURS_IN_SECONDS = 10800
UNWORKING_HOURS_DELAY = 60 # Время ожидания, чтобы не спамить в нерабочее время

# КОНСТАНТЫ НАМЕРЕНИЙ
INTENT_VISIT = 'ВИЗИТ'
INTENT_DIMENSIONS = 'ГАБАРИТЫ'
INTENT_CARE = 'УХОД'
INTENT_PRICE = 'ЦЕНА'
INTENT_DELIVERY = 'ДОСТАВКА'
INTENT_REGIONAL_DELIVERY = 'ДОСТАВКА_В_РЕГИОН'
INTENT_AVAILABILITY = 'НАЛИЧИЕ'
INTENT_UNWORKING_HOURS = 'НЕРАБОЧЕЕ_ВРЕМЯ'
INTENT_DISCOUNT = 'СКИДКА'
INTENT_COMPLETENESS = 'КОМПЛЕКТНОСТЬ'
INTENT_GREETINGS = 'ПРИВЕТСТВИЕ'
INTENT_OTHER = 'ДРУГОЕ'

# ШАБЛОНЫ СООБЩЕНИЙ БОТА
BOT_GREETING_MESSAGE = "Приветствуем Вас в нашем зеленом магазине, сейчас менеджер подключится и ответит на вопросы 🌿"
BOT_GREETING_MESSAGE_UNWORKING_HOURS = "Приветствуем Вас в нашем зеленом магазине, сейчас менеджеры спят. Ответим вам в рабочее время с 9 до 20 по МСК🌿"
BOT_CANT_ANSWER_MESSAGE = "К сожалению, я как бот могу ответить не на все вопросы. Зову менеджера."

RESPONSES = {
    INTENT_VISIT: """🏢 НАШ АДРЕС г. Москва, БЦ "Платформа", Спартаковский переулок, д.2, стр.1 6 подъезд, 4 этаж, офис 33
🚗 На территории БЦ для клиентов есть бесплатная парковка, чтобы воспользоваться парковкой, необходимо заранее заказать пропуск на въезд.
⏰ РЕЖИМ РАБОТЫ Каждый день: с 9:00 до 20:00.
Когда вас ожидать?""",
    INTENT_DIMENSIONS: """У нас есть множество вариантов размеров. Высота растения измеряется от пола и до последнего листочка, включая высоту кашпо.
Хотите подобрать растение?""",
    INTENT_CARE: """Вижу у вас вопросы по уходу, у нас есть услуга онлайн консультации. Она стоит 1700 руб, давайте оформим""",
    INTENT_PRICE: """Добрый день!
Сейчас я уточню цену и вернусь к вам""",
    INTENT_DELIVERY: """Можем отправить по Москве и области:
- Нашим курьером, вы получите растение в течении трех дней
- Яндекс доставкой в ближайшие сроки
С Авито доставкой мы не работаем.
Какой вариант интересует?""",
    INTENT_REGIONAL_DELIVERY: """Доставка в другие регионы осуществляется транспортными компаниями, по их ценам. Какое растение вас интересует?""",
    INTENT_AVAILABILITY: """Сейчас проверю наличие и вернусь к вам.""",
    INTENT_UNWORKING_HOURS: """Наши менеджеры сейчас отдыхают, но я отправлю запрос и утром мы вам ответим.""",
    INTENT_DISCOUNT: """На данный момент на эту позицию скидок, давайте посмотрим варианты по вашему бюджету. Подскажите, на какую сумму рассчитывали?""",
    INTENT_COMPLETENESS: """Вас интересует уже пересаженное растение или в техническом горшке?"""
}