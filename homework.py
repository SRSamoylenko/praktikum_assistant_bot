import logging.config
import os
import time

import requests
import telegram
from dotenv import load_dotenv
from pydantic import ValidationError
from requests.exceptions import ConnectionError, HTTPError

from config import EXCEPTION_TIME_TO_SLEEP, LOGGING_PARAMS, TIME_TO_SLEEP
from constants import HOMEWORK_VERDICTS, PRAKTIKUM_API_URL
from schemas import HomeworkData, Homeworks

logging.config.dictConfig(LOGGING_PARAMS)
load_dotenv()

try:
    PRAKTIKUM_TOKEN = os.environ['PRAKTIKUM_TOKEN']
    TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
    CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
except KeyError as e:
    logging.exception('Переменная окружения %s не найдена. '
                      'Запуск бота остановлен.', e)
    raise


def parse_homework_status(homework: HomeworkData) -> str:
    """Проверяет статус работы.
    Принимает на вход словарь с данными о домашней работе,
    возвращает строку, сообщающую о статусе работы.
    """
    logging.info('Парсинг домашней работы.')
    homework_name = homework.homework_name
    status = homework.status
    result = 'Статус работы изменился. Ответ содержит неизвестный статус'

    try:
        result = HOMEWORK_VERDICTS[status].format(homework_name=homework_name)
    except KeyError as e:
        logging.warning('Ответ содержит неизвестный статус: %s', e)

    return result


def get_homework_statuses(current_timestamp: int) -> Homeworks:
    """Возвращает словарь c текущей датой и списком домашних работ,
    статус которых изменился с момента current_timestamp.
    """
    logging.info('Запрос статуса домашних работ.')
    params = {'from_date': current_timestamp}
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    result = Homeworks(homeworks=[], current_date=None)

    try:
        homework_statuses = requests.get(
            PRAKTIKUM_API_URL,
            params=params,
            headers=headers,
        )
        homework_statuses.raise_for_status()
        result = Homeworks.parse_obj(homework_statuses.json())
    except HTTPError as e:
        logging.exception('Вернулся статус ответа: %s', e)
    except KeyError:
        logging.exception('Oтвет не содержит поля json.')
    except ValidationError:
        logging.exception('Сервер Яндекс.Практикума '
                          'не вернул ожидаемый ответ.')
    except ConnectionError:
        logging.exception('Не удалось соединиться '
                          'с сервером Яндекс.Практикума.')
    except Exception as e:
        logging.exception('Бот столкнулся с ошибкой '
                          'при запросе статуса домашних работ: %s', e)

    logging.info('Cтатусы домашних работ получены.')
    return result


def send_message(message: str, bot_client: telegram.Bot) -> telegram.Message:
    """Отправляет сообщение пользователю."""
    logging.info('Отправка сообщения')
    while True:
        try:
            return bot_client.send_message(CHAT_ID, message)
        except Exception as e:
            logging.exception('Возникла ошибка при отправке сообщения: %s', e)
            time.sleep(EXCEPTION_TIME_TO_SLEEP)


def main():
    logging.debug('Запуск бота')
    try:
        bot_client = telegram.Bot(token=TELEGRAM_TOKEN)
    except telegram.error.InvalidToken:
        logging.exception('Передан невалидный токен телеграм. '
                          'Запуск бота остановлен.')
        raise
    except telegram.error.NetworkError:
        logging.exception('Проблема с соединением. Запуск бота остановлен.')
        raise
    except telegram.error.TelegramError:
        logging.exception('Проблема со стороны сервера Telegram. '
                          'Запуск бота остановлен.')
        raise
    except Exception as e:
        logging.exception('Ошибка %s. Запуск бота остановлен.', e)
        raise
    current_timestamp = int(time.time())

    while True:
        updated_statuses = get_homework_statuses(current_timestamp)
        if updated_statuses.homeworks:
            logging.info('Имеются работы с обновленным статусом.')
            last_homework = updated_statuses.homeworks[0]
            message = parse_homework_status(last_homework)
            send_message(message, bot_client)
        else:
            logging.info('Работы с обновленным статусом отсутствуют.')
        current_timestamp = (updated_statuses.current_date
                             or current_timestamp)
        time.sleep(TIME_TO_SLEEP)


if __name__ == '__main__':
    main()
