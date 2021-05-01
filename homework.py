import logging
import os
import time
from logging.handlers import RotatingFileHandler
from typing import Dict, NewType

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE_FORMAT = '%(asctime)s, %(levelname)s, %(message)s, %(name)s'
LOG_CONSOLE_FORMAT = '%(levelname)s, %(message)s, %(name)s'

logging.basicConfig(
    level=logging.DEBUG,
    format=LOG_CONSOLE_FORMAT,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = RotatingFileHandler(
    BASE_DIR + f'/{__name__}.log',
    maxBytes=50000000,
    backupCount=5,
)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(LOG_FILE_FORMAT)
handler.setFormatter(formatter)

logger.addHandler(handler)

try:
    PRAKTIKUM_TOKEN = os.environ['PRAKTIKUM_TOKEN']
    TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
    CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
except KeyError as e:
    logger.exception(f'Переменная окружения {e} не найдена. '
                     f'Запуск бота остановлен.')

HOMEWORK_VERDICTS = {
    'approved': ('У вас проверили работу "{homework_name}"!\n\n'
                 'Ревьюеру всё понравилось, '
                 'можно приступать к следующему уроку.'),
    'rejected': ('У вас проверили работу "{homework_name}"!\n\n'
                 'К сожалению в работе нашлись ошибки.'),
    'reviewing': 'Работа {homework_name} взята на проверку.',
    'error': 'Ответ не содержит информации о статусе работы.',
}
TIME_TO_SLEEP = 300


HomeworkData = NewType('HomeworkData', Dict)

Homeworks = NewType('Homeworks', Dict)


def parse_homework_status(homework: HomeworkData) -> str:
    """Проверяет статус работы.
    Принимает на вход словарь с данными о домашней работе,
    возвращает строку, сообщающую о статусе работы.
    """
    homework_name = None
    status = 'error'
    result = 'Ошибка: Ответ содержит неизвестный статус'

    try:
        homework_name = homework['homework_name']
        status = homework['status']
    except KeyError as e:
        logger.exception(f'Ответ не содержит поля {e}.')

    try:
        result = HOMEWORK_VERDICTS[status].format(homework_name=homework_name)
    except KeyError as e:
        logger.exception(f'Ответ содержит неизвестный статус: {e}')

    return result


def get_homework_statuses(current_timestamp: int) -> Homeworks:
    """Возвращает словарь c текущей датой и списком домашних работ,
    статус которых изменился с момента current_timestamp.
    """
    params = {'from_date': current_timestamp}
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    result = {}

    try:
        homework_statuses = requests.get(
            'https://praktikum.yandex.ru/api/user_api/homework_statuses/',
            params=params,
            headers=headers,
        )
        result = homework_statuses.json()
    except AttributeError as e:
        logger.exception(f'homework_statuses не имеет аттрибута {e}.')

    return result


def send_message(message, bot_client):
    logger.info('Отправка сообщения')
    return bot_client.send_message(CHAT_ID, message)


def main():
    logger.debug('Запуск бота')
    bot_client = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            updated_statuses = get_homework_statuses(current_timestamp)
            if updated_statuses.get('homeworks'):
                last_homework = updated_statuses.get('homeworks')[0]
                message = parse_homework_status(last_homework)
                send_message(message, bot_client)
            current_timestamp = updated_statuses.get(
                'current_date',
                current_timestamp
            )
            time.sleep(TIME_TO_SLEEP)

        except Exception as e:
            logger.exception(e)
            send_message(f'Бот столкнулся с ошибкой: {e}', bot_client)
            time.sleep(5)


if __name__ == '__main__':
    main()
