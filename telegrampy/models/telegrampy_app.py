import logging
from asyncio import AbstractEventLoop
from typing import TYPE_CHECKING, Dict

from telegram import ReplyKeyboardMarkup
from telegram.ext import Application

from telegrampy.constants.text_constants import TEXT_REPLY_MARKUP, TEXT_CHAT_ID
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
        self._pending_keyboard_markup: Dict[int, Dict[str, ReplyKeyboardMarkup]] = {}
        self._application: Application = None
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

    def set_application(self, application):
        self._application: Application = application
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

    async def application_bot_send_message(self, **kwargs):
        if self._application is None:
            return
        reply_keyboard_markup: Dict[str, ReplyKeyboardMarkup] = self._pending_keyboard_markup.pop(kwargs[TEXT_CHAT_ID], None)

        if reply_keyboard_markup is not None:
            kwargs[TEXT_REPLY_MARKUP] = reply_keyboard_markup
        await self._application.bot.send_message(**kwargs)

    def add_pending_keyboard_markup(self, chat_id: int, markup: ReplyKeyboardMarkup):
        if isinstance(markup, ReplyKeyboardMarkup):
            self._pending_keyboard_markup[chat_id] = markup
