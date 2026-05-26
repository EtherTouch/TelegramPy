import json
import random
from typing import Dict, List, Union

from telegrampy.constants.file_constants import DEFAULT_CONFIG_JSON
from telegrampy.constants.text_constants import TEXT_TASK_S, TEXT_USER_S, TEXT_FLASK_API_ADDRESS, TEXT_BOT_TOKEN, TEXT_GREETING_S, TEXT_CHAT_STYLE, TEXT_RKM, TEXT_IKM, TEXT_INIT_MSG, TEXT_PROC_TITLE
from telegrampy.models.ip_port import IpPort
from telegrampy.models.taskdetails import TaskDetails
from telegrampy.models.telegrampy_app import TelegramPyApp
from telegrampy.models.user import User


class Configuration:
    def __init__(self, config_file: str = None):
        if config_file is None:
            config_file = DEFAULT_CONFIG_JSON
        with open(config_file, "r") as reader:
            self._config_json = json.loads(reader.read())
            # TODO Check config json is a valid config json

        # lets parse other fields
        self._flask_ip_port: IpPort = IpPort(self._config_json[TEXT_FLASK_API_ADDRESS])
        self._bot_token: str = self._config_json[TEXT_BOT_TOKEN]

        self._proc_title = "telegrampy"
        if TEXT_PROC_TITLE in self._config_json:
            self._proc_title = self._config_json[TEXT_PROC_TITLE]

        self._init_msg: List[str] = []
        if TEXT_INIT_MSG in self._config_json:
            self._init_msg = self._config_json[TEXT_INIT_MSG]

        self._greetings = self._config_json[TEXT_GREETING_S]
        self._chat_style: str = self._config_json[TEXT_CHAT_STYLE].lower()
        if not (self._chat_style == TEXT_RKM or self._chat_style == TEXT_IKM):
            raise Exception(f"chat_style should be \"{TEXT_RKM}\" or \"{TEXT_IKM}\"")

    def parse_tasks(self, telegram_py_app: TelegramPyApp):
        # let's parse what tasks are there
        _task_dict: Dict[str, TaskDetails] = {}
        for name, task_detail in self._config_json[TEXT_TASK_S].items():
            _task_dict[name] = TaskDetails(name, task_detail, telegram_py_app)

        # lets parse users
        self._users: Dict[int, User] = {}
        self._admin_users: Dict[int, User] = {}
        for user in self._config_json[TEXT_USER_S]:
            user_obj = User(user, _task_dict)
            self._users[user_obj.chat_id] = user_obj
            if user_obj.is_admin:
                self._admin_users[user_obj.chat_id] = user_obj

    @property
    def proc_title(self) -> str:
        return self._proc_title

    @property
    def users(self) -> Dict[int, User]:
        return self._users

    @property
    def admin_users(self) -> Dict[int, User]:
        return self._admin_users

    @property
    def flask_ip_port(self) -> IpPort:
        return self._flask_ip_port

    @property
    def bot_token(self) -> str:
        return self._bot_token

    @property
    def random_init_msg(self) -> Union[str, None]:
        if len(self._init_msg) == 0:
            return None
        return random.choice(self._init_msg)

    @property
    def greetings(self) -> List[str]:
        return self._greetings

    @property
    def chat_style(self) -> str:
        return self._chat_style
