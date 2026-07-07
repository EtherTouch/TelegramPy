import logging

import requests

from telegrampy.configuration import Configuration
from telegrampy.util.log_util import getlogger
from telegrampy.util.util import add_hmac_headers

logger = getlogger(__name__, logging.DEBUG)


def test_update_via_api_call():
    data_to_send = {
        "data": {
            "msg": "Hello world!"
        }
    }
    headers = {}
    # add_hmac_headers(headers, b"SomeSecretKey")
    # r = requests.post(f"http://127.0.0.1:4212/update", headers=headers, json=data_to_send)

    config = Configuration()
    add_hmac_headers(headers, config.flask_hmac_auth_key)
    r = requests.post(f"http://127.0.0.1:{config.flask_ip_port.port}/update", headers=headers, json=data_to_send)

    print(f"satus_code: {r.status_code}; response: \"{r.text.strip()}\"")
    pass


if __name__ == '__main__':
    test_update_via_api_call()
