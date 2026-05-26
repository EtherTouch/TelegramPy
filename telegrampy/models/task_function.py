from typing import Dict


class TaskFunction:

    def __init__(self, task_json: Dict):
        self._function_name = task_json["function"]
        self._function_alias = task_json["alias"] if "alias" in task_json else None
        self._is_kwarg_func: bool = False
        self._is_async_function = False
        pass

    @property
    def function_name(self) -> str:
        return self._function_name

    @property
    def alias_function_name(self) -> str:
        return self._function_alias

    @property
    def common_name(self) -> str:
        if self._function_alias is not None:
            return self._function_alias
        else:
            return self._function_name

    @property
    def is_kwarg_func(self) -> bool:
        return self._is_kwarg_func

    def set_is_kwarg_func(self):
        self._is_kwarg_func = True
        pass
    @property
    def is_async_func(self) -> bool:
        return self._is_async_function
    def set_is_async_func(self):
        self._is_async_function = True
        pass
