import asyncio
import inspect
import logging
from typing import Dict

from telegrampy.constants.text_constants import TEXT_MAX_COLUMN
from telegrampy.executor.executor_helper import ExecutorHelper
from telegrampy.models.task_function import TaskFunction
from telegrampy.models.telegrampy_app import TelegramPyApp
from telegrampy.util.log_util import getlogger
from telegrampy.util.util import has_kwargs_parameter

logger = getlogger(__name__, logging.DEBUG)


class TaskDetails:

    def __init__(self, name: str, task_json, telegram_py_app: TelegramPyApp):
        self._async_lock = asyncio.Lock()
        self._name = name.strip()  # this is the class name in .py file
        self._telegram_py_app = telegram_py_app
        self._task_description = task_json["desc"] if "desc" in task_json else self._name
        self._task_alias_name = task_json["alias"] if "alias" in task_json else None
        self._max_keyboard_coulumn = task_json[TEXT_MAX_COLUMN] if TEXT_MAX_COLUMN in task_json else None
        # if it is not singleton we will call the class for each user id
        self._is_singleton = task_json["singleton"] if "singleton" in task_json else False
        self._common_name_functions: Dict[str, TaskFunction] = {}
        for function in task_json["functions"]:
            task_function = TaskFunction(function)
            self._common_name_functions[task_function.common_name] = task_function
        # lets check **kwarg parametre exist in the function and also async function
        _tmp_obj = ExecutorHelper.load_task(self.name, self._telegram_py_app)

        kwarg_containing_func = set()
        async_func = set()
        for attr_name in dir(_tmp_obj):
            if attr_name.startswith("_"):
                continue
            attr = getattr(_tmp_obj, attr_name)
            if callable(attr):
                if has_kwargs_parameter(attr):
                    kwarg_containing_func.add(attr_name)
                if inspect.iscoroutinefunction(attr):
                    async_func.add(attr_name)
        for k, v in self._common_name_functions.items():
            if v.function_name in kwarg_containing_func:
                v.set_is_kwarg_func()
            if v.function_name in async_func:
                v.set_is_async_func()
        # end of doing searching kwarg functions

        if self._is_singleton:
            # store the created object if it is a singleton
            self._object = _tmp_obj
        else:
            self._object = {}

    async def get_task_object(self, chat_id):
        # this help preventing searching and loading object dynamically as it will consume time to read files again and again
        if self._is_singleton:
            return self._object

        if chat_id in self._object:
            return self._object[chat_id]

        # run blocking work outside event loop
        obj = await asyncio.to_thread(
            ExecutorHelper.load_task,
            self.name,
            self._telegram_py_app
        )

        async with self._async_lock:
            if chat_id not in self._object:
                self._object[chat_id] = obj
            return self._object[chat_id]

    @property
    def max_keyboard_coulumn(self):
        return self._max_keyboard_coulumn

    @property
    def name(self) -> str:
        return self._name

    @property
    def common_name(self):
        if self._task_alias_name is not None:
            return self._task_alias_name
        else:
            return self._name

    @property
    def task_description(self):
        return self._task_description

    @property
    def common_name_functions(self) -> Dict[str, TaskFunction]:
        return self._common_name_functions
