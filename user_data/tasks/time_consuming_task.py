import threading
import time

from telegrampy.conversation_handler.chat_state import TaskDone

"""
- This example use running a time blocking task in another thread
- N.B. the task called by telegrampy of a class's function should not take time. if time is taken run in a seperate thread or preocess
"""


class TimeConsumingTask:

    def blocking_function(self):
        print("Blocking function")
        time.sleep(10)
        print(f"End of blocking function")

    def run_in_a_thread(self):
        threading.Thread(target=self.blocking_function, daemon=True).start()
        return TaskDone("Blocking function is running in another thread")
