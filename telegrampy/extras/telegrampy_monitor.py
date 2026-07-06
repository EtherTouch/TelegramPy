import logging
import subprocess
import time

import psutil

from telegrampy.configuration import Configuration
from telegrampy.util.log_util import getlogger
from telegrampy.util.util import generate_proc_title

logger = getlogger(__name__, logging.DEBUG)


# This script is intended for Raspberry Pi OS only. It monitors TelegramPy
# And reboots the Raspberry Pi if TelegramPy stops running.

def is_process_exists(keyword: str) -> bool:
    for proc in psutil.process_iter(["name", "cmdline"]):
        try:
            cmd = " ".join(proc.info["cmdline"] or [])
            if keyword in cmd:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False


def current_epoch_seconds():
    return int(time.time())


if __name__ == '__main__':
    logger.info("Wait for 5 minute to start monitoring")
    time.sleep(300)

    configuration: Configuration = Configuration()
    proctitle_name = generate_proc_title(configuration)
    last_telegrampy_is_running_epoch = current_epoch_seconds()
    while True:
        if is_process_exists(proctitle_name):
            logger.info(f"\"{proctitle_name}\" is running")
            last_telegrampy_is_running_epoch = current_epoch_seconds()
        else:
            logger.error(f"\"{proctitle_name}\" is not running")
            pass
        time.sleep(30)
        if (current_epoch_seconds() - last_telegrampy_is_running_epoch) > 300:
            logger.error(f"\"{proctitle_name}\" is not running more than 5 minute")
            break
    logger.warning(f"Rebooting in 60 seconds")
    time.sleep(60)
    subprocess.run(["sudo", "reboot"], check=True)
