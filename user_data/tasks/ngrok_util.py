import re
import subprocess
import threading
import time
import requests

from telegrampy.conversation_handler.chat_state import WaitingArgument, TaskDoneWithError
from telegrampy.models.meta_data import MetaData


class NgrokProcessHelper:

    def __init__(self):
        self._ngrok_subprocess = None
        self._tcp_url_pattern = r'url=(tcp://[^\s]+)'
        pass

    @property
    def ngrok_subprocess(self):
        return self._ngrok_subprocess

    def start_ngrok(self, *args):
        meta_data: MetaData = args[0]
        command = ["/usr/local/bin/ngrok", "tcp", "22", "--log=stdout"]
        self._ngrok_subprocess = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for line in self._ngrok_subprocess.stdout:
            # print(line)
            if "\"started tunnel\"" in line:
                match = re.search(self._tcp_url_pattern, line)
                if not match:
                    continue
                url = match.group(1)
                self._threaded_send_update(meta_data, f"Ngrok running at:\n{url}")
                time.sleep(1.5)
                self._threaded_send_update(meta_data, f"@{url.split('//')[1].split(':')[0]} -p {url.split(':')[2]} -o ServerAliveInterval=60 -o ServerAliveCountMax=3")

    def _threaded_send_update(self, metadata: MetaData, msg):
        threading.Thread(target=self._send_update, args=[metadata, msg, ], daemon=True).start()

    def _send_update(self, metadata: MetaData, msg):
        meta_data_json = metadata.to_json()
        url = metadata.update_addr
        data = {
            "meta": meta_data_json,
            "data": {
                "msg": msg
            }
        }
        response = requests.post(url, json=data)
        p = response

    def kill(self, metadata: MetaData):
        if self._ngrok_subprocess is None:
            self._threaded_send_update(metadata, "There is no ngrok subprocess")
            return
        self._ngrok_subprocess.kill()
        self._ngrok_subprocess = None
        self._threaded_send_update(metadata, "Ngrok process has closed.")
        pass


class NgrokUtil:
    def __init__(self):
        self._ngrok_process_helper = NgrokProcessHelper()
        pass

    def _convert_to_seconds(self, time_str):
        """
        Convert a time string with units (e.g., "1H", "2h", "30m") to seconds.
        Supports hours (H, h) and minutes (M, m).
        """
        time_str = time_str.strip().upper()  # Normalize the input
        if time_str.endswith('H'):
            try:
                hours = float(time_str[:-1])
                return hours * 3600  # Convert hours to seconds
            except ValueError:
                raise ValueError("Invalid number format for hours.")
        elif time_str.endswith('M'):
            try:
                minutes = float(time_str[:-1])
                return minutes * 60  # Convert minutes to seconds
            except ValueError:
                raise ValueError("Invalid number format for minutes.")
        elif time_str.endswith('S'):
            try:
                seconds = float(time_str[:-1])
                return seconds  # Convert minutes to seconds
            except ValueError:
                raise ValueError("Invalid number format for minutes.")
        else:
            try:
                seconds = float(time_str)
                return seconds
            except ValueError:
                raise ValueError("Unsupported time unit. Use 'H' for hours or 'M' for minutes.")

    def start(self, *args, **kwargs):
        if (self._ngrok_process_helper.ngrok_subprocess is not None):
            return TaskDoneWithError("Another ngrok subprocess has been running.")
        # Simple example to pass arguments in a function
        if len(args) < 1:
            return WaitingArgument("How long ngrok will run")
        try:
            time_to_wait = self._convert_to_seconds(args[0])
        except Exception as e:
            return TaskDoneWithError(str(e))
        metadata = kwargs.get("metadata")
        threading.Thread(target=self._ngrok_process_helper.start_ngrok, args=[metadata, ], daemon=True).start()
        # kill the process after sometime
        timer = threading.Timer(time_to_wait, self._ngrok_process_helper.kill, args=[metadata, ])
        timer.start()

    def stop_ngrok(self, **kwargs):
        metadata = kwargs.get("metadata")
        self._ngrok_process_helper.kill(metadata)



"""
Add this Json file in config.json5

  "tasks": {
    "NgrokUtil": {
      "desc": "Ngrok wrapper",
      "singleton": true,
      "functions": [
        {
          "function": "start",
          "alias": "Start Ngrok"
        },
        {
          "function": "stop_ngrok",
          "alias": "Stop Ngrok"
        }
      ]
    }
  }
"""
