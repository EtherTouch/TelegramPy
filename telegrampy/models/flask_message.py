from typing import Dict

from telegrampy.constants.text_constants import TEXT_DATA, TEXT_MSG
from telegrampy.models.meta_data import MetaData


class FlaskMessage:

    def __init__(self, json_data):
        self._meta_data: MetaData = MetaData.from_flask_message(json_data)
        self._data: Dict = json_data[TEXT_DATA]
        self._message = self._data[TEXT_MSG]

    @property
    def meta_data(self) -> MetaData:
        return self._meta_data

    @property
    def message(self) -> str:
        return self._message
