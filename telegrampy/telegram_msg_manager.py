import asyncio
import logging
from typing import List

from telegram import Update, Message, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import ContextTypes, Application

from telegrampy.constants.text_constants import TEXT_REPLY_MARKUP, TEXT_TEXT
from telegrampy.conversation_handler.conversation_handler import ConversationHandler
from telegrampy.models.flask_message import FlaskMessage
from telegrampy.models.telegrampy_app import TelegramPyApp
from telegrampy.util.authorisation_util import check_authorisation
from telegrampy.util.log_util import getlogger
from telegrampy.util.util import query_message_wrapper

logger = getlogger(__name__, logging.DEBUG)


class TelegramMsgManager:

    def __init__(self, application: Application, telegram_py_app: TelegramPyApp):
        self._telegram_py_app = telegram_py_app
        self._configuration = telegram_py_app.configuration
        self._application: Application = application
        self._conversation_handler: ConversationHandler = ConversationHandler(telegram_py_app)

    async def unauth_handle_telegram_update_msg(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        # lets get the chat id
        if update.callback_query:
            chat_id = int(update.callback_query.message.chat.id)
        else:
            chat_id = int(update.message.chat_id)
        # check this chat_id is authorised
        if check_authorisation(chat_id, self._configuration):
            await self._handle_telegram_update_msg(update, context)
        else:
            logger.error('Rejected unauthorized message from chatid: %s', chat_id)
            self.send_message_to_admins(f'Rejected unauthorized message from chatid: {chat_id}')
        pass

    async def _handle_telegram_update_msg(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.message is not None:
            logger.info(f"Received Valid message: {update.message.text} from {update.message.chat_id}")
            chat_id, reply = await self._conversation_handler.receive_conversation(
                update,
                update.message.chat_id,
                update.message.text,
                context)
            result: Message | None = None
            if len(reply[TEXT_TEXT]) > 0:
                try:
                    result: Message = await self._application.bot.send_message(
                        chat_id=chat_id, **reply
                    )
                except Exception as e:
                    logger.error(f"{str(e)} | [ChatID > {chat_id}]")
                    return
                pass
            # lets store the message id if the reply markup is empty
            reply_markup: InlineKeyboardMarkup = reply[TEXT_REPLY_MARKUP]
            if isinstance(reply_markup, InlineKeyboardMarkup) and len(reply_markup.inline_keyboard) != 0:
                if result is not None:
                    self._conversation_handler.latest_query_msg_ids[chat_id] = result.message_id
        elif update.callback_query is not None:
            query: CallbackQuery = update.callback_query
            chat_id = query.from_user.id
            # CallbackQueries need to be answered, even if no notification to the user is needed
            # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
            await query.answer()
            # lets check if the query is the latest query
            if chat_id not in self._conversation_handler.latest_query_msg_ids:
                self._conversation_handler.latest_query_msg_ids[chat_id] = query.message.message_id
            else:
                last_query_id = self._conversation_handler.latest_query_msg_ids[chat_id]
                if last_query_id > query.message.message_id:
                    try:
                        query_message: Message = query.message
                        query_text_message = query_message.text
                        logger.warning(f"Old query id: {query.message.message_id}")
                        # collapse the inline keyboard and do nothing
                        await query.edit_message_text(
                            **{
                                TEXT_TEXT: query_text_message,
                                TEXT_REPLY_MARKUP: InlineKeyboardMarkup(())
                            }
                        )
                    except Exception as e:
                        pass
                    return

            chat_id, reply = await self._conversation_handler.receive_conversation(
                update,
                query.from_user.id,
                query.data,
                context)
            # modify the query
            await query.edit_message_text(**reply)

    async def eqit_query_message(self, message_id: int, chat_id: int, message: str):
        # replace some characters
        # message = message.replace("_", "\\_").replace("*", "\\*").replace("`", "\\`")
        # message = message.replace("*", "\\*").replace("`", "\\`")
        # get the curent reply markup
        reply = await self._conversation_handler.reply_maker.get_reply(chat_id)
        _cor = self._application.bot.edit_message_text(
            text=message,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=reply[TEXT_REPLY_MARKUP]
        )
        try:
            asyncio.get_running_loop()
            asyncio.create_task(_cor)
        except:
            asyncio.run_coroutine_threadsafe(_cor, self._telegram_py_app.event_loop)
            return

    async def _safe_send_to_bot(self, chat_id, message):
        try:
            await self._application.bot.send_message(chat_id, message)
        except Exception as e:
            logger.error(f"{str(e)} | [ChatID > {chat_id}]")
            pass

    def send_message(self, chat_id: int, message: str):
        # replace some characters
        # message = message.replace("_", "\\_").replace("*", "\\*").replace("`", "\\`")
        # message = message.replace("*", "\\*").replace("`", "\\`")

        _cor = self._safe_send_to_bot(
            chat_id,
            message
        )
        try:
            asyncio.get_running_loop()
            asyncio.create_task(_cor)
        except:
            asyncio.run_coroutine_threadsafe(_cor, self._telegram_py_app.event_loop)
            return

    def send_message_to_chat_ids(self, chat_ids: List[int], message: str):
        # replace some characters
        # message = message.replace("_", "\\_").replace("*", "\\*").replace("`", "\\`")
        # message = message.replace("*", "\\*").replace("`", "\\`")

        has_event_loop = True
        try:
            asyncio.get_running_loop()
        except:
            has_event_loop = False

        for chat_id in chat_ids:
            _cor = self._safe_send_to_bot(
                chat_id,
                message
            )
            if has_event_loop:
                asyncio.create_task(_cor)
                continue
            else:
                asyncio.run_coroutine_threadsafe(_cor, self._telegram_py_app.event_loop)
                continue

    def send_message_to_admins(self, message):
        admin_user_chat_ids: List[int] = list(self._configuration.admin_users.keys())
        self.send_message_to_chat_ids(admin_user_chat_ids, message)

    def update_from_flask(self, flask_msg: FlaskMessage) -> None:
        if flask_msg.meta_data is None:
            # if there is no metadata send the message to admin
            self.send_message_to_admins(flask_msg.message)
        else:
            chat_ids = flask_msg.meta_data.chat_ids if flask_msg.meta_data.chat_ids is not None else []
            if flask_msg.meta_data.query_message:
                query_chat_id = flask_msg.meta_data.query_message.chat_id
                query_msg_id = flask_msg.meta_data.query_message.message_id
                # remove from chat ids as message is send
                chat_ids.remove(query_chat_id) if query_chat_id in chat_ids else None
                # todo edit the query message
                _cor = self.eqit_query_message(
                    message_id=query_msg_id,
                    chat_id=query_chat_id,
                    message=query_message_wrapper(flask_msg.message)
                )

                asyncio.get_running_loop()
                asyncio.create_task(_cor)
                pass
            if flask_msg.meta_data.simple_message:
                simple_chat_id = flask_msg.meta_data.simple_message.chat_id
                # remove from chat ids as message is send
                chat_ids.remove(simple_chat_id) if simple_chat_id in chat_ids else None
                self.send_message(chat_id=simple_chat_id, message=flask_msg.message)
            # send the mesage to the remaining chat ids
            self.send_message_to_chat_ids(chat_ids=chat_ids, message=flask_msg.message)

        pass
