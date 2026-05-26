import logging

from telegrampy.models.meta_data import MetaData
from telegrampy.models.telegrampy_app import TelegramPyApp
from telegrampy.util.log_util import getlogger

logger = getlogger(__name__, logging.DEBUG)


class TelegramTask:

    def __init__(self):
        self._telegram_py_app: TelegramPyApp | None = None
        pass

    def set_telegram_py_app(self, telegram_py_app):
        self._telegram_py_app = telegram_py_app

    def send_message(self, message: str, metadata: MetaData = None):
        if self._telegram_py_app is None:
            logger.error(f"self._telegram_py_app is not set yet")
            return
        self._telegram_py_app.send_telegram_message(message, metadata)

        pass

    def send_message_to_admins(self, message: str):
        if self._telegram_py_app is None:
            logger.error(f"self._telegram_py_app is not set yet")
            return
        self._telegram_py_app.send_telegram_message_to_admins(message)

        pass
