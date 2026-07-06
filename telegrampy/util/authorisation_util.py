import logging

from telegrampy.configuration import Configuration
from telegrampy.util.log_util import getlogger

logger = getlogger(__name__, logging.DEBUG)


def check_authorisation(chat_id: int, configuration: Configuration):
    # Check if the chat_id is authorized
    flag_valid_chat_id = chat_id in configuration.valid_user_chat_ids
    if not flag_valid_chat_id:
        # logger.error('Rejected unauthorized message from chatid: %s', chat_id)
        return False
    else:
        return True
