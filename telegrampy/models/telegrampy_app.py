import logging
from asyncio import AbstractEventLoop
from typing import TYPE_CHECKING

from telegrampy.models.meta_data import MetaData
from telegrampy.util.log_util import getlogger

if TYPE_CHECKING:
    from telegrampy.configuration import Configuration
    from telegrampy.telegram_msg_manager import TelegramMsgManager

logger = getlogger(__name__, logging.DEBUG)


class TelegramPyApp:

    def __init__(self, event_loop):
        self._configuration: 'Configuration' = None
        self._telegram_msg_manager: 'TelegramMsgManager' = None
        self._event_loop: AbstractEventLoop = event_loop
        pass

    @property
    def configuration(self) -> 'Configuration':
        return self._configuration

    @property
    def event_loop(self) -> AbstractEventLoop:
        return self._event_loop

    # @property
    # def telegram_msg_manager(self) -> 'TelegramMsgManager':
    #     return self._telegram_msg_manager

    def set_configuration(self, configuration: 'Configuration'):
        self._configuration = configuration
        pass

    def set_telegram_msg_manager(self, telegram_msg_manager: 'TelegramMsgManager'):
        self._telegram_msg_manager = telegram_msg_manager
        pass

    def send_telegram_message(self, message: str, metadata: MetaData = None):
        metadata_chat_ids = metadata.chat_ids
        if metadata is None:
            logger.error(f"Metadata is none. Sent \"{message}\" to admins")
            self._telegram_msg_manager.send_message_to_admins(message)
            return
        else:
            self._telegram_msg_manager.send_message_to_chat_ids(metadata_chat_ids, message)
        pass

    def send_telegram_message_to_admins(self, message: str):
        self._telegram_msg_manager.send_message_to_admins(message)
        pass
