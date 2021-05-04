import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE_DIR = os.path.join(BASE_DIR, 'praktikum_assistant.log')
FILE_LOG_FORMAT = '%(asctime)s, %(levelname)s, %(message)s, %(name)s'
CONSOLE_LOG_FORMAT = '%(levelname)s, %(message)s, %(name)s'

LOGGING_PARAMS = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': CONSOLE_LOG_FORMAT,
        },
        'file': {
            'format': FILE_LOG_FORMAT,
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
            'level': 'DEBUG',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_FILE_DIR,
            'maxBytes': 100000,
            'backupCount': 5,
            'formatter': 'file',
            'level': 'DEBUG',
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console', 'file'],
    }
}

TIME_TO_SLEEP = 300
EXCEPTION_TIME_TO_SLEEP = 30
