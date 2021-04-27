import logging
import os
import time
from enum import Enum
from logging.handlers import RotatingFileHandler
from typing import Dict, NewType

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FORMAT = '%(asctime)s, %(levelname)s, %(message)s, %(name)s'


class HomeworkStatus(Enum):
    APPROVED = 'approved'
    REJECTED = 'rejected'
    REVIEWING = 'reviewing'


HomeworkData = NewType('HomeworkData', Dict)

Homeworks = NewType('Homeworks', Dict)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = RotatingFileHandler(
    BASE_DIR + f'/{__name__}.log',
    maxBytes=50000000,
    backupCount=5,
)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(LOG_FORMAT)
handler.setFormatter(formatter)

logger.addHandler(handler)


def parse_homework_status(homework: HomeworkData) -> str:
    """Проверяет статус работы.
    Принимает на вход словарь с данными о домашней работе,
    возвращает строку, сообщающую о статусе работы.
    """
    homework_name = homework.get('homework_name')
    status = homework.get('status')
    if HomeworkStatus(status) is HomeworkStatus.REJECTED:
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = ('Ревьюеру всё понравилось, '
                   'можно приступать к следующему уроку.')
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp: int) -> Homeworks:
    """Возвращает словарь c текущей датой и списком домашних работ,
    статус которых изменился с момента current_timestamp.
    """
    params = {'from_date': current_timestamp}
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    homework_statuses = requests.get(
        'https://praktikum.yandex.ru/api/user_api/homework_statuses/',
        params=params,
        headers=headers,
    )
    return homework_statuses.json()


def send_message(message, bot_client):
    logger.info('Отправка сообщения')
    return bot_client.send_message(CHAT_ID, message)


def main():
    logger.debug('Запуск бота')
    bot_client = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(0)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(new_homework.get('homeworks')[0]),
                    bot_client,
                )
            current_timestamp = new_homework.get(
                'current_date',
                current_timestamp
            )
            time.sleep(300)

        except Exception as e:
            logger.exception(e)
            send_message(f'Бот столкнулся с ошибкой: {e}', bot_client)
            time.sleep(5)


if __name__ == '__main__':
    main()
