import logging
from typing import Dict

from telegram import Update

from telegrampy.configuration import Configuration
from telegrampy.constants.text_constants import TEXT_BACK, TEXT_SLASH_START
from telegrampy.conversation_handler.chat import Chat
from telegrampy.conversation_handler.chat_state import WaitingArgument
from telegrampy.models.telegrampy_app import TelegramPyApp
from telegrampy.models.user import User
from telegrampy.util.log_util import getlogger

logger = getlogger(__name__, logging.DEBUG)


class ChatProgress:

    def __init__(self, telegram_py_app: TelegramPyApp):
        self._chat_progress: Dict[int, Chat] = {}
        self._telegram_py_app: TelegramPyApp = telegram_py_app
        self._configuration: Configuration = self._telegram_py_app.configuration
        pass

    async def add_chat_progress(self, update: Update, chat_id: int, message: str):
        message = message.strip()

        if chat_id not in self._chat_progress:
            self._chat_progress[chat_id] = Chat(chat_id, self._telegram_py_app)
            return
        chat = self._chat_progress[chat_id]
        chat_state_cur = await chat.chat_state()
        # if message == TEXT_SLASH_START and not isinstance(chat_state_cur, WaitingArgument):
        if message == TEXT_SLASH_START:
            self.reset_chat_progress(chat_id)
            return
        elif message == TEXT_BACK and not isinstance(chat_state_cur, WaitingArgument):
            if chat_id in self._chat_progress:
                self._chat_progress[chat_id]._go_back()
                return
        else:
            user: User = self._configuration.users[chat_id]
            # add message and execute function
            await self._chat_progress[chat_id].add_message(update, user, message)

    def reset_chat_progress(self, chat_id: int):
        self._chat_progress[chat_id]._reset()

    def get_chat(self, chat_id: int) -> Chat:
        if chat_id not in self._chat_progress:
            self._chat_progress[chat_id] = Chat(chat_id, self._telegram_py_app)
        return self._chat_progress[chat_id]
