import hashlib
import hmac
import inspect
import os
import socket
import time
from datetime import datetime
from http import HTTPStatus
from typing import List, Set, Tuple, MutableMapping

from flask import Response, jsonify
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, \
    ReplyKeyboardRemove
from telegram._utils.types import ReplyMarkup

from telegrampy.constants.text_constants import TEXT_STATUS, TEXT_MSG


def get_formatted_datetime() -> str:
    # Get the current date and time
    now = datetime.now()

    # Format the date and time as required, with abbreviated month names
    formatted_date_time = "{:%d-%b-%Y %H:%M:%S:%f}".format(now)[:-3]

    return formatted_date_time


def get_ip(ip: str):
    if not ip == '0.0.0.0':
        return ip
    try:
        # Create a socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connect to Google's public DNS server 8.8.8.8 on port 80
        s.connect(('8.8.8.8', 80))
        # Get the local IP address bound to the socket
        local_ip = s.getsockname()[0]
        # Close the socket connection
        s.close()
        return local_ip
    except socket.error:
        return '127.0.0.1'  # Fallback to localhost if unable to determine IP


def has_kwargs_parameter(func) -> bool:
    signature = inspect.signature(func)
    parameters = signature.parameters.values()
    for param in parameters:
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            return True
    return False


# Utility for making Keyboard and buttons
# For measuring word length
# Define character widths for a-z, A-Z, 0-9, symbols, space, and tab (adjust as needed)
character_widths = {
    'a': 1, 'b': 1, 'c': 1, 'd': 1, 'e': 1, 'f': 1, 'g': 1, 'h': 1, 'i': 0.7, 'j': 1,
    'k': 1, 'l': 1, 'm': 1, 'n': 1, 'o': 1, 'p': 1, 'q': 1, 'r': 1, 's': 1, 't': 1,
    'u': 1, 'v': 1, 'w': 1, 'x': 1, 'y': 1, 'z': 1,
    'A': 1.2, 'B': 1.2, 'C': 1.2, 'D': 1.2, 'E': 1.2, 'F': 1.2, 'G': 1.2, 'H': 1.2, 'I': 0.7, 'J': 1,
    'K': 1.2, 'L': 1.2, 'M': 1.4, 'N': 1.2, 'O': 1.4, 'P': 1.2, 'Q': 1.4, 'R': 1.2, 'S': 1.2, 'T': 1.2,
    'U': 1.2, 'V': 1.2, 'W': 1.6, 'X': 1.2, 'Y': 1.2, 'Z': 1.2,
    '0': 1, '1': 1, '2': 1, '3': 1, '4': 1, '5': 1, '6': 1, '7': 1, '8': 1, '9': 1,
    '!': 0.6, '@': 1.4, '#': 1.4, '$': 1.4, '%': 1.4, '^': 1, '&': 1.4, '*': 1, '(': 1, ')': 1,
    '-': 1, '_': 1, '=': 1, '+': 1, '[': 1, ']': 1, '{': 1, '}': 1, ';': 0.7, ':': 0.7,
    '"': 0.8, "'": 0.5, '\\': 1, '|': 0.6, ',': 0.6, '.': 0.6, '/': 0.8, '<': 1, '>': 1, '?': 1,
    '~': 1, '`': 0.6,
    ' ': 0.5,  # Space
    '\t': 1  # Tab
}


def measure_displayed_length(text):
    # Calculate total width based on character widths
    total_width = sum(character_widths.get(char, 1) for char in text)

    return total_width


def inline_keyboard_button_maker(opt: str):
    return InlineKeyboardButton(opt, callback_data=opt)


def make_inline_keyboard_markup(options: List[str], *args) -> ReplyMarkup:
    # max word count per row is 35
    # for s in options:
    #     print(
    #         f"{s} = {measure_displayed_length(s)}"
    #     )

    # inline_keyboard = [InlineKeyboardButton(str(opt), callback_data=str(opt)) for opt in options]
    # max_row_count = 3
    # keyboard = [inline_keyboard[i:i + max_row_count] for i in range(0, len(inline_keyboard), max_row_count)]

    keyboard = keyboard_maker_logic2(options, 30, inline_keyboard_button_maker)
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def make_reply_keyboard_markup(options: List[str], max_keyboard_coulumn) -> ReplyMarkup:
    # max word count per row is 38
    # for s in options:
    #     print(
    #         f"{s} = {measure_displayed_length(s)}"
    #     )

    if len(options) == 0:
        # remove the ReplyKeyboardMarkup
        return ReplyKeyboardRemove()

    # inline_keyboard = [KeyboardButton(str(opt)) for opt in options]
    # max_row_count = 3
    # keyboard = [inline_keyboard[i:i + max_row_count] for i in range(0, len(inline_keyboard), max_row_count)]
    #
    if max_keyboard_coulumn is None:
        keyboard = keyboard_maker_logic1(options, 38, KeyboardButton)
    else:
        inline_keyboard = [KeyboardButton(str(opt)) for opt in options]
        keyboard = [inline_keyboard[i:i + max_keyboard_coulumn] for i in
                    range(0, len(inline_keyboard), max_keyboard_coulumn)]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    return reply_markup


def keyboard_maker_logic1(options: List[str], max_length_per_row: int, button):
    keyboard = []
    current_row = []
    usable_row_width = max_length_per_row
    for word in options:
        word_length = measure_displayed_length(word) + 2.2  # two unit for padding
        if usable_row_width == max_length_per_row:
            # no new button added at the row
            usable_row_width = usable_row_width - word_length
            current_row.append(button(str(word)))
        elif usable_row_width < max_length_per_row:
            if word_length > usable_row_width:
                # some button existed in the row and the wordlength dont fit
                # so append the previous row to keyboard
                # and  make a new row
                keyboard.append(current_row)
                usable_row_width = max_length_per_row
                current_row = []
                # append the word
                usable_row_width = usable_row_width - word_length
                current_row.append(button(str(word)))
            else:
                usable_row_width = usable_row_width - word_length
                current_row.append(button(str(word)))
        else:
            raise Exception("This should not be called")
    if len(current_row) > 0:
        keyboard.append(current_row)
    return keyboard


def keyboard_maker_logic2(options: List[str], max_length_per_row: int, button):
    keyboard = []
    current_row = []
    usable_row_width = max_length_per_row
    for word in options:
        word_length = measure_displayed_length(word) + 2.2  # two unit for padding
        if usable_row_width / 2 < word_length:
            current_row.append(button(str(word)))
            keyboard.append(current_row)
            # make new row in next
            current_row = []
            usable_row_width = max_length_per_row
        else:
            current_row.append(button(str(word)))
            usable_row_width = usable_row_width - word_length

    if len(current_row) > 0:
        keyboard.append(current_row)
    return keyboard


# End of Utility for making Keyboard and buttons


def query_message_wrapper(message: str) -> str:
    return f"{get_formatted_datetime()}\n\n{message}"


def do_nothing_message_wrapper(message: str) -> str:
    return message


def get_this_device_local_ip_addresses() -> Set[str]:
    local_ips: Set[str] = {
        "127.0.0.1",
    }
    if os.name != "posix":
        import socket

        hostname = socket.gethostname()
        try:
            # Add all IPv4 addresses assigned to this host
            for info in socket.getaddrinfo(hostname, None, socket.AF_INET):
                local_ips.add(info[4][0])
        except socket.gaierror:
            pass

        return local_ips
    else:

        import socket
        import fcntl
        import struct
        import array
        max_interfaces = 128
        bytes_ = max_interfaces * 32

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        names = array.array('B', b'\0' * bytes_)

        outbytes = struct.unpack(
            'iL',
            fcntl.ioctl(
                sock.fileno(),
                0x8912,  # SIOCGIFCONF
                struct.pack('iL', bytes_, names.buffer_info()[0])
            )
        )[0]

        names_as_str = names.tobytes()

        for i in range(0, outbytes, 40):
            ip = socket.inet_ntoa(names_as_str[i + 20:i + 24])
            local_ips.add(ip)

        return local_ips


def verify_flask_hmac_request_auth(request_headers, hmac_auth_key: bytes, validity_milli_sec: int) -> Tuple[bool, Response | None, int, str]:
    timestamp_header = request_headers.get("Request-Timestamp")
    authorization_header = request_headers.get("Authorization")

    if not timestamp_header or not authorization_header:
        return False, jsonify({TEXT_STATUS: False, TEXT_MSG: "Missing headers"}), HTTPStatus.BAD_REQUEST, "Missing headers"

    try:
        # Expected format:
        # Authorization: HMAC-SHA256 <signature>
        parts = authorization_header.split(" ", 1)

        if len(parts) != 2 or parts[0] != "HMAC-SHA256":
            return False, jsonify({TEXT_STATUS: False, "msg": "Invalid authorization format"}), HTTPStatus.UNAUTHORIZED, "Invalid authorization format"
        client_signature = parts[1]
    except Exception as e:
        return False, jsonify({TEXT_STATUS: False, "msg": "Invalid authorization header"}), HTTPStatus.UNAUTHORIZED, f"Invalid authorization header: {str(e)}"

    # Check timestamp freshness (prevent replay attacks)
    try:
        current_time = int(time.time() * 1000)
        ts = int(timestamp_header)
        if ts > current_time + validity_milli_sec:  # 3 sec window
            return False, jsonify({TEXT_STATUS: False, TEXT_MSG: "Request auth token invalid"}), HTTPStatus.UNAUTHORIZED, "Request auth token too early"
        if current_time - ts > validity_milli_sec:  # 3 sec window
            return False, jsonify({TEXT_STATUS: False, TEXT_MSG: "Request auth token expired"}), HTTPStatus.UNAUTHORIZED, "Request auth token expired"
    except Exception as e:
        return False, jsonify({TEXT_STATUS: False, TEXT_MSG: "Invalid timestamp"}), HTTPStatus.BAD_REQUEST, f"Invalid timestamp: {str(e)}"
    # Verify signature
    expected_signature = hmac.new(hmac_auth_key, timestamp_header.encode("utf-8"), hashlib.sha256).hexdigest()

    # Compare hashes securely
    if not hmac.compare_digest(expected_signature, client_signature):
        return False, jsonify({TEXT_STATUS: False, TEXT_MSG: "Unauthorized"}), HTTPStatus.UNAUTHORIZED, "Unauthorized"

    return True, None, HTTPStatus.OK, "Authorized"


def add_hmac_headers(headers: MutableMapping[str, str], hmac_auth_key: bytes) -> None:
    """
    Add HMAC authentication headers to an existing headers mapping.
    """
    timestamp = str(int(time.time() * 1000))

    signature = hmac.new(hmac_auth_key, timestamp.encode("utf-8"), hashlib.sha256).hexdigest()
    headers["Request-Timestamp"] = timestamp
    headers["Authorization"] = f"HMAC-SHA256 {signature}"
