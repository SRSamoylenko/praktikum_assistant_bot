# praktikum_assistant_bot
Telegram бот, оповещающий об изменении статуса домашних работ в Яндекс.Практикуме.

## Стек технологий
python 3, python-telegram-bot

## Установка и настройка бота
1. Проверьте установлен ли интерпретатор Python.
2. Клонируйте репозиторий и перейдите в папку проекта, для этого в консоли наберите:
    ```
    git clone https://github.com/SRSamoylenko/praktikum_assistant_bot
    cd praktikum_assistant_bot
    ```
3. Создайте файл `.env` и запишите в него необходимые переменные окружения:
    ```
    touch .env
    vim .env
    ```
    В файле запишите:
    ```
    PRAKTIKUM_TOKEN=<токен Яндекс.Практикум>
    TELEGRAM_TOKEN=<токен телеграм-бота>
    TELEGRAM_CHAT_ID=<id чата телеграм>
    ```
4. Создайте и активируйте виртуальное окружение:
    ```
    python3 -m venv venv
    source ./venv/bin/activate
    ```
5. Установите зависимости:
    ```
    pip install -r requirements.txt
    ```

## Запуск бота
Для запуска бота введите команду:
```
python homework.py
```
