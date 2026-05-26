import threading

import requests
from pathos.multiprocessing import ProcessingPool

from telegrampy.configuration import Configuration
from telegrampy.conversation_handler.chat_state import TaskDone
from telegrampy.models.meta_data import MetaData
from telegrampy.models.telegrampy_app import TelegramPyApp

"""
This example includes:
- Running cpu bound task.
- Update a message when task is complete through api of the running flask server.

"""


def cpu_bound_function(*args):
    # Note: to make it work with ProcessingPool, it has to pass objects that can be picklable
    print("Starting CPU-bound task")
    # Simulate a CPU-bound operation
    sum(range(5 * (10 ** 8)))  # This is a placeholder for a CPU-bound operation
    print(f"CPU-bound task completed")
    if (len(args) < 1):
        return
    # let's post update message to the telegram via the flask server
    # we have passed the metadata as argument in *args
    meta_data: MetaData = args[0]
    meta_data_json = meta_data.to_json()

    # url = "http://localhost:4212/update"
    url = f"http://localhost:{Configuration().flask_ip_port.port}/update"
    data = {
        "meta": meta_data_json,
        "data": {
            "msg": "Cpu bound task completed \n[update through flask api]"
        }
    }

    response = requests.post(url, json=data)
    print(response.json(), f" [{response.status_code}]")
    return ":)", meta_data


class CpuBoundTask:

    def __init__(self):
        self._telegram_py_app: TelegramPyApp = None
        pass

    def run_in_a_thread(self):
        # Don't do this, this will still block the main thread because it is cpu bound
        # Lol this will still block the main thread. you should run such in another process
        threading.Thread(target=cpu_bound_function, daemon=True).start()
        return TaskDone("Cpu bound task is running in another thread")

    # Run the cpu bound function in another process
    # Using "multiprocess" library will cause some Pickling error
    def run_in_a_process(self, **kwargs):
        metadata = kwargs.get("metadata")
        self._telegram_py_app = kwargs.get("app")
        self._telegram_py_app.send_telegram_message("Trying to start \n[update without using flask api]", metadata)

        with ProcessingPool() as pool:
            result = pool.apipe(cpu_bound_function, metadata)

            def watcher():
                value = result.get()  # blocks ONLY in this thread
                self.process_done(value)

            threading.Thread(target=watcher, daemon=True).start()
        return TaskDone("Cpu bound task running in another process")

    def process_done(self, value):
        result, metadata = value
        print("Process finished with result:", result)
        # Reply to telegram
        self._telegram_py_app.send_telegram_message("Cpu bound task completed \n[update without using flask api]", metadata)
        self._telegram_py_app.send_telegram_message_to_admins("Cpu bound task completed[admins] \n[update without using flask api]")
