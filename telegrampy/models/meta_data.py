from typing import Dict, List, Optional

from telegram import Update

from telegrampy.constants.text_constants import TEXT_META, TEXT_CHAT_ID_S, TEXT_MESSAGE_ID, TEXT_QUERY_MSG, \
    TEXT_SIMPLE_MSG, TEXT_CHAT_ID, TEXT_UPDATE_ADDR


class QueryMessage:
    def __init__(self, message_id: int, chat_id: int):
        self._chat_id: int = chat_id
        self._message_id: int = message_id

    @property
    def chat_id(self) -> int:
        return self._chat_id

    @property
    def message_id(self) -> int:
        return self._message_id

    def to_json(self):
        return {
            TEXT_CHAT_ID: self._chat_id,
            TEXT_MESSAGE_ID: self._message_id,
        }


class SimpleMessage:
    def __init__(self, message_id: int, chat_id: int):
        self._chat_id: int = chat_id
        self._message_id = message_id

    @property
    def chat_id(self) -> int:
        return self._chat_id

    @property
    def message_id(self) -> int:
        return self._message_id

    def to_json(self):
        return {
            TEXT_CHAT_ID: self._chat_id,
            TEXT_MESSAGE_ID: self._message_id,
        }


class MetaData(dict):
    update_addr = ""  # static variable to store flask update address

    def __init__(self, chat_ids: Optional[List[int]], query_message: QueryMessage = None,
                 simple_message: SimpleMessage = None, update_addr=""):
        self._chat_ids: List[int] = chat_ids
        self._query_message = query_message
        self._simple_message = simple_message
        self._update_addr = update_addr
        super().__init__(self.to_json())

    @property
    def chat_ids(self) -> List[int]:
        chat_ids = []
        if self._chat_ids is not None:
            chat_ids.extend(self._chat_ids)

        if self._query_message is not None and self._query_message.chat_id is not None:
            chat_ids.append(self._query_message.chat_id)
        if self._simple_message is not None and self._simple_message.chat_id is not None:
            chat_ids.append(self._simple_message.chat_id)

        chat_ids = list(set(chat_ids))
        return chat_ids

    @property
    def query_message(self) -> Optional[QueryMessage]:
        return self._query_message

    @property
    def simple_message(self) -> Optional[SimpleMessage]:
        return self._simple_message

    def to_json(self):
        data = {
            TEXT_UPDATE_ADDR: self._update_addr,
            TEXT_CHAT_ID_S: self._chat_ids,
            TEXT_QUERY_MSG: self._query_message.to_json() if self._query_message is not None else None,
            TEXT_SIMPLE_MSG: self._simple_message.to_json() if self._simple_message is not None else None,
        }
        # delete None data
        data = {k: v for k, v in data.items() if v is not None}
        return data

    @classmethod
    def from_flask_message(cls, data_json: Dict):
        try:
            meta_data = data_json[TEXT_META]
            chat_ids: List[int] = meta_data[TEXT_CHAT_ID_S] if TEXT_CHAT_ID_S in meta_data else None
            update_addr: str = meta_data[TEXT_UPDATE_ADDR] if TEXT_UPDATE_ADDR in meta_data else MetaData.update_addr
            query_message = QueryMessage(**meta_data[TEXT_QUERY_MSG]) if TEXT_QUERY_MSG in meta_data else None
            simple_message = SimpleMessage(**meta_data[TEXT_SIMPLE_MSG]) if TEXT_SIMPLE_MSG in meta_data else None
            return cls(chat_ids=chat_ids, query_message=query_message, simple_message=simple_message, update_addr=update_addr)
        except Exception:
            return None

    @classmethod
    def from_telegram_update(cls, update: Update):
        query_message = None
        simple_message = None
        if update.callback_query:
            chat_id = int(update.callback_query.message.chat.id)
            query_message = QueryMessage(message_id=update.callback_query.message.message_id, chat_id=chat_id)
        else:
            chat_id = int(update.message.chat_id)
            simple_message = SimpleMessage(message_id=update.message.message_id, chat_id=chat_id)
        return cls(chat_ids=None, query_message=query_message, simple_message=simple_message, update_addr=MetaData.update_addr)
