import random
from typing import Dict, List, Union, Set

import json5

from telegrampy.constants.file_constants import DEFAULT_CONFIG_JSON
from telegrampy.constants.text_constants import TEXT_TASK_S, TEXT_USER_S, TEXT_FLASK_API_ADDRESS, TEXT_BOT_TOKEN, TEXT_GREETING_S, TEXT_CHAT_STYLE, TEXT_RKM, TEXT_IKM, TEXT_INIT_MSG, TEXT_PROC_TITLE, TEXT_FLASK_API_ALLOWED_IP, TEXT_LOCALHOST, TEXT_FLASK_HMAC_AUTH_KEY, TEXT_HMAC_REQUEST_VALIDITY_MS
from telegrampy.models.ip_port import IpPort
from telegrampy.models.taskdetails import TaskDetails
from telegrampy.models.telegrampy_app import TelegramPyApp
from telegrampy.models.user import User
from telegrampy.util.util import get_this_device_local_ip_addresses


class Configuration:
    def __init__(self, config_file: str = None):
        if config_file is None:
            config_file = DEFAULT_CONFIG_JSON
        with open(config_file, "r", encoding="utf-8") as reader:
            self._config_json = json5.load(reader)
            # TODO Check config json5 is a valid config json5

        # lets parse other fields
        self._flask_ip_port: IpPort = IpPort(self._config_json[TEXT_FLASK_API_ADDRESS])
        if TEXT_FLASK_API_ALLOWED_IP in self._config_json:
            allowed_ip_addresses: Set[str] = set(self._config_json[TEXT_FLASK_API_ALLOWED_IP])
            if TEXT_LOCALHOST in allowed_ip_addresses:
                allowed_ip_addresses = allowed_ip_addresses.union(get_this_device_local_ip_addresses())
            else:
                allowed_ip_addresses.add("127.0.0.1")
            self._allowed_ip_addresses: Set[str] | None = allowed_ip_addresses
        else:
            self._allowed_ip_addresses: Set[str] | None = None
        if TEXT_FLASK_HMAC_AUTH_KEY in self._config_json:
            self._flask_hmac_auth_key: bytes | None = self._config_json[TEXT_FLASK_HMAC_AUTH_KEY].encode("utf-8")
            self._hmac_request_validity_ms: int = self._config_json[TEXT_HMAC_REQUEST_VALIDITY_MS]
        else:
            self._flask_hmac_auth_key: str | None = None
            self._hmac_request_validity_ms: int = 0

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
        self._valid_user_chat_id: Set[int] = set()
        for user in self._config_json[TEXT_USER_S]:
            user_obj = User(user, _task_dict)
            self._valid_user_chat_id.add(user_obj.chat_id)
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
    def valid_user_chat_ids(self) -> Set[int]:
        return self._valid_user_chat_id

    @property
    def admin_users(self) -> Dict[int, User]:
        return self._admin_users

    @property
    def flask_ip_port(self) -> IpPort:
        return self._flask_ip_port

    @property
    def allowed_ip_addresses(self) -> Set[str] | None:
        return self._allowed_ip_addresses

    @property
    def flask_hmac_auth_key(self) -> bytes | None:
        return self._flask_hmac_auth_key

    @property
    def hmac_request_validity_ms(self) -> int:
        return self._hmac_request_validity_ms

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
