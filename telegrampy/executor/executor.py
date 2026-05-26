import logging
from typing import List

from telegram import Update

from telegrampy.conversation_handler.chat_state import TaskDoneWithError, TaskDone, \
    TaskNotDoneWithTaskNameError, TaskNotDoneWithFuncNameError, ChatState
from telegrampy.models.meta_data import MetaData
from telegrampy.models.taskdetails import TaskDetails
from telegrampy.models.task_function import TaskFunction
from telegrampy.models.telegrampy_app import TelegramPyApp
from telegrampy.models.user import User
from telegrampy.util.log_util import getlogger

logger = getlogger(__name__, logging.DEBUG)


def func_safe_wrapper(f, message: str = ""):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as error:
            logger.exception(
                f"[{message}]: Unexpected error {error} calling {f}"
            )
            return TaskDoneWithError(f"[{message}]: Unexpected error {error} calling {f}")

    return wrapper


def async_func_safe_wrapper(f, message: str = ""):
    async def wrapper(*args, **kwargs):
        try:
            return await f(*args, **kwargs)
        except Exception as error:
            logger.exception(
                f"[{message}]: Unexpected error {error} calling {f}"
            )
            return TaskDoneWithError(f"[{message}]: Unexpected error {error} calling {f}")

    return wrapper


class Executor:
    @staticmethod
    async def execute(update: Update, user: User, conversation: List[str], telegram_py_app: TelegramPyApp):
        common_task_name = conversation[0]
        common_function_name = conversation[1]
        arguments = conversation[2:]
        # will raise exception if the task is not in the user's valid tasks
        task: TaskDetails = user.common_name_tasks[common_task_name]
        function: TaskFunction = task.common_name_functions[common_function_name]
        chat_id = user.chat_id
        obj = await task.get_task_object(chat_id)
        if obj is None:
            return TaskNotDoneWithTaskNameError(f"Unable to load taskname \"{common_task_name}\"")
        executable_function_name = function.function_name
        try:
            callable_func = getattr(obj, executable_function_name)
        except AttributeError as e:
            return TaskNotDoneWithFuncNameError(str(e))
        if function.is_kwarg_func:
            # lets pass extra parametre if it has **kwargs
            # TODO pass chat meta data
            kwargs = {
                "metadata": MetaData.from_telegram_update(update),
                "app": telegram_py_app,
                # "telegram_py_app": telegram_py_app,
            }
        else:
            kwargs = {}

        if function.is_async_func:
            return_val = await  async_func_safe_wrapper(callable_func, task.name)(*arguments, **kwargs)
        else:
            return_val = func_safe_wrapper(callable_func, task.name)(*arguments, **kwargs)
        # else:
        #     if function.is_async_func:
        #         return_val = await async_func_safe_wrapper(callable_func, task.name)(*arguments)
        #     else:
        #         return_val = func_safe_wrapper(callable_func, task.name)(*arguments)
        if not isinstance(return_val, ChatState):
            return_val = TaskDone(f"Done {function.common_name}")
        return return_val
