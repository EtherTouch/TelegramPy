class ChatState:

    def __init__(self, message: str | None):
        if isinstance(message, str):
            self._message_raw: str | None = message.strip()
        else:
            self._message_raw: str | None = message
        pass

    @property
    def message_raw(self) -> str | None:
        return self._message_raw

    @property
    def message(self) -> str:
        if self._message_raw is None:
            return ""
        return self._message_raw

    def is_message_empty(self):
        return self._message_raw == ""


class WaitingPyClass(ChatState):

    def __init__(self, message: str = ""):
        super().__init__(message)

    pass


class WaitingFunction(ChatState):
    def __init__(self, message: str | None = ""):
        super().__init__(message)

    pass


class WaitingArgument(ChatState):
    def __init__(self, message: str = ""):
        super().__init__(message)

    pass


class TaskDoneWithError(ChatState):
    def __init__(self, message: str = ""):
        super().__init__(message)

    pass


class TaskDone(ChatState):
    def __init__(self, message: str | None = ""):
        super().__init__(message)

    pass


class TaskCompletelyDone(ChatState):
    def __init__(self, message: str = ""):
        super().__init__(message)

    pass


class TaskNotDoneWithTaskNameError(ChatState):
    def __init__(self, message: str = ""):
        super().__init__(message)

    pass


class TaskNotDoneWithFuncNameError(ChatState):
    def __init__(self, message: str = ""):
        super().__init__(message)

    pass
