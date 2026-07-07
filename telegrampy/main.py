import asyncio
import logging
from datetime import datetime

from setproctitle import setproctitle
from telegram.ext import Application, MessageHandler, filters, CallbackQueryHandler

from telegrampy.configuration import Configuration
from telegrampy.constants.text_constants import TEXT_IKM, TEXT_RKM
from telegrampy.flask_server import FlaskServer
from telegrampy.models.telegrampy_app import TelegramPyApp
from telegrampy.telegram_msg_manager import TelegramMsgManager
from telegrampy.util.log_util import getlogger
from telegrampy.util.util import generate_proc_title

logger = getlogger(__name__, logging.DEBUG)

if __name__ == '__main__':
    configuration: Configuration = Configuration()
    setproctitle(generate_proc_title(configuration))
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    telegram_py_app = TelegramPyApp(loop)
    # lets parse the configuration
    configuration.parse_tasks(telegram_py_app)
    telegram_py_app.set_configuration(configuration)

    # Let's make telegram bot application
    application = Application.builder().token(configuration.bot_token).build()
    telegram_py_app.set_application(application)
    telegram_bot_wrapper = TelegramMsgManager(application, telegram_py_app)
    telegram_py_app.set_telegram_msg_manager(telegram_bot_wrapper)

    # lets attached the handler according to the chat style
    if configuration.chat_style == TEXT_IKM:
        application.add_handler(MessageHandler(filters.TEXT, telegram_bot_wrapper.unauth_handle_telegram_update_msg))
        application.add_handler(CallbackQueryHandler(telegram_bot_wrapper.unauth_handle_telegram_update_msg))
    elif configuration.chat_style == TEXT_RKM:
        # Don't register CallbackQueryHandler if style is TEXT_RKM
        application.add_handler(MessageHandler(filters.TEXT, telegram_bot_wrapper.unauth_handle_telegram_update_msg))

    # lets make flask server app
    # make callback as "update_from_flask"
    flask_server = FlaskServer(configuration, telegram_bot_wrapper.update_from_flask, loop)
    # Now serve the flask server
    flask_server.serve()

    random_init_msg = configuration.random_init_msg
    if random_init_msg is not None:
        telegram_bot_wrapper.send_message_to_admins(f'[{datetime.now().strftime("%d %b %Y %H:%M:%S.%f")[:-3]}]\n{random_init_msg}')

    # Now run polling
    application.run_polling(
        drop_pending_updates=True,  # we dont want to take message which were already sent before bot started
        timeout=30
    )
