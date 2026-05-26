"""
This example show
- Features of TaskDone(None) which don't reply when this task is done
- Reply to users directly by extending task with 'TelegramTask'
"""
from telegrampy.conversation_handler.chat_state import TaskDone
from telegrampy.models.telegram_task import TelegramTask


class ExtraExample(TelegramTask):

    def no_reply_on_task_done(self):
        print("Done no reply on task done")
        return TaskDone(None)

    def reply_to_users_directly(self, **kwargs):
        metadata = kwargs.get("metadata")
        print("Replying directly")
        if metadata is None:
            self.send_message("Hello users[metadata is none]", metadata)
        else:
            self.send_message("Hello users[metadata is not none]", metadata)

    def reply_to_users_directly_alt(self, metadata, **kwargs):
        print("Replying directly_alt")
        if metadata is None:
            self.send_message("Hello users from Alt [metadata is none]", metadata)
        else:
            self.send_message("Hello users from Alt [metadata is not none]", metadata)

    def reply_directly_to_admins(self):
        print("Replying directly to admins")
        self.send_message_to_admins("Hello admins")
