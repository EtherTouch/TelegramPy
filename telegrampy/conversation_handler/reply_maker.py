import random
from typing import List, Dict, Callable

from telegrampy.configuration import Configuration
from telegrampy.constants.text_constants import TEXT_BACK, TEXT_REPLY_MARKUP, TEXT_TEXT, TEXT_RKM, TEXT_IKM
from telegrampy.conversation_handler.chat_progress import ChatProgress
from telegrampy.conversation_handler.chat_state import WaitingPyClass, WaitingFunction, WaitingArgument
from telegrampy.models.taskdetails import TaskDetails
from telegrampy.models.task_function import TaskFunction
from telegrampy.util.util import make_inline_keyboard_markup, make_reply_keyboard_markup, \
    do_nothing_message_wrapper, query_message_wrapper


class ReplyMaker:
    def __init__(self, configuration: Configuration, chat_progress: ChatProgress):
        self._configuration = configuration
        self._chat_progresss = chat_progress
        # choose type of keyboard maker acordung to the style
        if self._configuration.chat_style == TEXT_RKM:
            self._keyboard_maker: Callable = make_reply_keyboard_markup
            self._message_wrapper: Callable = do_nothing_message_wrapper
        elif self._configuration.chat_style == TEXT_IKM:
            self._keyboard_maker: Callable = make_inline_keyboard_markup
            self._message_wrapper: Callable = query_message_wrapper
        pass

    async def get_reply(self, chat_id: int):
        chat = self._chat_progresss.get_chat(chat_id)
        message: str = ""
        options: List[str] = []
        common_name_task_dict: Dict[str, TaskDetails] = self._configuration.users[chat_id].common_name_tasks
        max_keyboard_column = None
        chat_state_cur=await chat.chat_state()
        if isinstance(chat_state_cur, WaitingPyClass):
            # lets check if any message stored in the chat state
            if chat_state_cur.is_message_empty():
                message = random.choice(self._configuration.greetings)
            else:
                message = chat_state_cur.message
            options = list(common_name_task_dict.keys())
        elif isinstance(chat_state_cur, WaitingFunction):
            task_name = await chat.get_last_message()
            if task_name is None:
                # this must not be called
                raise Exception("There was no last messsage")
            task: TaskDetails = common_name_task_dict[task_name]
            # lets check if any message stored in the chat state
            if chat_state_cur.is_message_empty():
                message = task.task_description
            else:
                message = chat_state_cur.message
            task_functions: Dict[str, TaskFunction] = task.common_name_functions
            options = list(task_functions.keys())
            options.append(TEXT_BACK)
            max_keyboard_column = task.max_keyboard_coulumn
        elif isinstance(chat_state_cur, WaitingArgument):
            message = chat_state_cur.message

        reply_markup = self._keyboard_maker(options, max_keyboard_column)
        message = self._message_wrapper(message)
        return {
            TEXT_TEXT: message,
            TEXT_REPLY_MARKUP: reply_markup
        }
