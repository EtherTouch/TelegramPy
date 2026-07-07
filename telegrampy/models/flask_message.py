from typing import Dict

from telegrampy.models.meta_data import MetaData


class FlaskMessage:

    def __init__(self, json_data):
        self._meta_data: MetaData = MetaData.from_flask_message(json_data)
        self._data: Dict = json_data["data"]
        self._message = self._data["msg"]

    @property
    def meta_data(self) -> MetaData:
        return self._meta_data

    @property
    def message(self) -> str:
        return self._message
