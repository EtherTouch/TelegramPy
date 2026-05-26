import asyncio
import json
import logging
from typing import List, Optional, Any

from telegram import Update

from telegrampy.conversation_handler.chat_state import WaitingPyClass, WaitingArgument, WaitingFunction, ChatState, \
    TaskCompletelyDone, TaskDone, TaskDoneWithError, TaskNotDoneWithTaskNameError, TaskNotDoneWithFuncNameError
from telegrampy.executor.executor import Executor
from telegrampy.models.telegrampy_app import TelegramPyApp
from telegrampy.models.user import User
from telegrampy.util.log_util import getlogger

logger = getlogger(__name__, logging.DEBUG)


class Chat:
    def __init__(self, chat_id, telegram_py_app: TelegramPyApp):
        self._telegram_py_app: TelegramPyApp = telegram_py_app
        self._chat_id = chat_id
        self._chat_state = WaitingPyClass()
        self._chat_messages: List[str] = []
        self._async_lock = asyncio.Lock()
        pass

    def _reset(self):
        self._chat_state = WaitingPyClass()
        self._chat_messages: List[str] = []

    def _go_back(self):
        if len(self._chat_messages) == 0:
            self._chat_state = WaitingPyClass()
            return
        # remove the last message
        self._chat_messages.pop()
        # update the chat state
        if isinstance(self._chat_state, WaitingArgument):
            self._chat_state = WaitingFunction()
        elif isinstance(self._chat_state, WaitingFunction):
            self._chat_state = WaitingPyClass()

    async def _add_message(self, update: Update, user: User, message: str):
        # for logging purpose
        __msg = self._chat_messages.copy()
        __msg.append(message)
        logger.debug(f"Messages: {json.dumps(__msg)}")
        # end of logging
        stripped_message = message.strip()
        return_value: ChatState | Any = None
        if isinstance(self._chat_state, WaitingPyClass):
            # check if it is valid task, then add
            if stripped_message in user.common_name_tasks:
                self._chat_messages.append(message.strip())
                self._chat_state = WaitingFunction()
            else:
                self._chat_state = WaitingPyClass(f"\"{stripped_message}\" is not a valid task.")
                pass
        elif isinstance(self._chat_state, WaitingFunction):
            # Lets check if it is valid funtion, last message will be a valid task name
            if stripped_message in user.common_name_tasks[self._chat_messages[-1]].common_name_functions:
                self._chat_messages.append(message.strip())
                # Lets execute the function
                return_value = await Executor.execute(update, user, self._chat_messages, self._telegram_py_app)
            else:
                self._chat_state = WaitingFunction(
                    f"\"{stripped_message}\" is not a valid function in \"{self._chat_messages[-1]}\"")
            pass
        elif isinstance(self._chat_state, WaitingArgument):
            self._chat_messages.append(message.strip())
            return_value = await Executor.execute(update, user, self._chat_messages, self._telegram_py_app)
            pass
        # if the task was executed, return value is not None
        if return_value is None:
            return
        # The following lines are for after task is executed
        return_type: ChatState = type(return_value)

        if return_type == TaskCompletelyDone:
            # we have to reset
            self._reset()
            # now store the message
            self._chat_state = WaitingPyClass(return_value.message)
        elif return_type == TaskDone:
            self._chat_state = WaitingFunction(return_value.message_raw)
            self._chat_messages = self._chat_messages[:1]
        elif return_type == TaskDoneWithError:
            self._chat_state = WaitingFunction(return_value.message)
            self._chat_messages = self._chat_messages[:1]
        elif return_type == WaitingArgument:
            self._chat_state = return_value
        # if there was an error handle it
        elif return_type == TaskNotDoneWithTaskNameError:
            self._chat_state = WaitingPyClass(return_value.message)  # change the chat state class
            self._reset()
        elif return_type == TaskNotDoneWithFuncNameError:
            self._chat_state = WaitingFunction(return_value.message)  # change the chat state class
            self._chat_messages = self._chat_messages[:1]  # remove the last message which is a function name

    async def chat_state(self) -> ChatState:
        async with self._async_lock:
            return self._chat_state

    async def add_message(self, update: Update, user: User, message: str):
        async with self._async_lock:
            await self._add_message(update, user, message)

    async def get_last_message(self) -> Optional[str]:
        async with self._async_lock:
            if len(self._chat_messages) > 0:
                return self._chat_messages[-1]
            else:
                return None
