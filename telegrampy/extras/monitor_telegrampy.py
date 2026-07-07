import logging
import subprocess
import time
from http import HTTPStatus
from multiprocessing import Process, Queue
from queue import Empty

import requests

from telegrampy.configuration import Configuration
from telegrampy.util.log_util import getlogger

# This script is intended for Raspberry Pi OS only. It monitors TelegramPy
# And reboots the Raspberry Pi if TelegramPy stops running.
logger = getlogger(__name__, logging.DEBUG)


def _worker(url: str, queue: Queue):
    try:
        response = requests.get(url)

        if response.status_code != HTTPStatus.OK:
            queue.put((False, f"HTTP {response.status_code}"))
            return

        data = response.json()
        queue.put((True, data.get("status") is True))

    except Exception as e:
        queue.put((False, str(e)))


def _is_process_running(url_for_status: str) -> bool:
    queue = Queue()
    process = Process(target=_worker, args=(url_for_status, queue))
    process.start()

    process.join(timeout=10)
    if process.is_alive():
        logger.error("Status check exceeded 10 seconds. Killing process.")
        process.terminate()
        process.join()
        return False

    try:
        success, result = queue.get_nowait()
        if success:
            return result
        logger.error(result)
        return False
    except Empty:
        return False


def current_epoch_seconds():
    return int(time.time())


if __name__ == '__main__':
    logger.info("wait for 5 minute to start monitoring")
    time.sleep(300)

    configuration: Configuration = Configuration()
    status_url = f"http://127.0.0.1:{configuration.flask_ip_port.port}/status"

    last_ok = current_epoch_seconds()
    while True:
        logger.info(f"checking telegrampy is running or not")
        if _is_process_running(status_url):
            logger.info(f"telegrampy is running")
            last_ok = current_epoch_seconds()
        else:
            logger.error(f"telegrampy is not running")
            pass
        now = current_epoch_seconds()
        if now - last_ok > 300:
            logger.error(f"telegrampy is not running more than 5 minute")
            break
        time.sleep(10)

    logger.warning(f"Rebooting in 60 seconds")
    time.sleep(60)
    subprocess.run(["sudo", "reboot"], check=True)
