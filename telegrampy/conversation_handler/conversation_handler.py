from typing import Dict

from telegram import Update
from telegram.ext import ContextTypes

from telegrampy.conversation_handler.chat_progress import ChatProgress
from telegrampy.conversation_handler.reply_maker import ReplyMaker
from telegrampy.models.telegrampy_app import TelegramPyApp


class ConversationHandler:

    def __init__(self, telegram_py_app: TelegramPyApp):
        self._telegram_py_app: TelegramPyApp = telegram_py_app
        self._configuration = telegram_py_app.configuration
        self._chat_porgress = ChatProgress(telegram_py_app)
        self._reply_maker: ReplyMaker = ReplyMaker(self._configuration, self._chat_porgress)
        self._latest_query_msg_ids: Dict[int, int] = {}  # we store message id to filtre out latest message
        pass

    async def receive_conversation(self, update: Update, chat_id: int, message: str, context: ContextTypes.DEFAULT_TYPE) -> (
            int, Dict):
        await self._chat_porgress.add_chat_progress(update, chat_id, message)
        # get replay layout
        reply = await self._reply_maker.get_reply(chat_id)
        # Replace the text with the message from return value
        return chat_id, reply

    @property
    def latest_query_msg_ids(self):
        return self._latest_query_msg_ids

    @property
    def reply_maker(self) -> ReplyMaker:
        return self._reply_maker
