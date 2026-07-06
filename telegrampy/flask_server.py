import logging
from http import HTTPStatus
from typing import Callable

import uvicorn
from asgiref.wsgi import WsgiToAsgi
from flask import Flask, request, jsonify

from telegrampy.configuration import Configuration
from telegrampy.constants.text_constants import TEXT_STATUS, TEXT_MSG, TEXT_POST_CAP, TEXT_SLASH_UPDATE, \
    TEXT_SLASH_UPDATE_SLASH, TEXT_SLASH_STATUS, TEXT_SLASH_STATUS_SLASH, TEXT_GET_CAP
from telegrampy.models.flask_message import FlaskMessage
from telegrampy.models.meta_data import MetaData
from telegrampy.util.log_util import getlogger
from telegrampy.util.util import get_ip, verify_flask_hmac_request_auth

logger = getlogger(__name__, logging.DEBUG)


class FlaskServer:
    def __init__(self, configuration: Configuration, callback: Callable, event_loop):
        self._configuration = configuration
        self._callback = callback
        self._event_loop = event_loop
        self._flask_app = Flask(__name__)
        self._register()
        self._flag_check_request_origin_ip: bool = configuration.allowed_ip_addresses is not None
        self._allowed_ip_addresses = configuration.allowed_ip_addresses

        self._flag_check_hmac_auth_signature: bool = configuration.flask_hmac_auth_key is not None
        self._flask_hmac_auth_key = configuration.flask_hmac_auth_key
        self._hmac_request_validity_ms: int = configuration.hmac_request_validity_ms

        pass

    def _register(self):

        @self._flask_app.route(TEXT_SLASH_UPDATE, methods=[TEXT_POST_CAP])
        @self._flask_app.route(TEXT_SLASH_UPDATE_SLASH, methods=[TEXT_POST_CAP])
        async def custom_updates():
            # check the origin ip is from valid one
            if self._flag_check_request_origin_ip:
                client_ip = request.remote_addr
                if client_ip not in self._allowed_ip_addresses:
                    logger.error(f"Forbidden api call from  \"{client_ip}\"")
                    return jsonify({TEXT_STATUS: False, "message": "Forbidden"}), HTTPStatus.FORBIDDEN
                pass

            # check if signature is valid
            if self._flag_check_hmac_auth_signature:
                auth_status, json_response, response_status, log_message = verify_flask_hmac_request_auth(request.headers, self._flask_hmac_auth_key, self._hmac_request_validity_ms)
                if not auth_status:
                    logger.error(log_message)
                    return json_response, response_status
                pass
            # A valid message received

            if request.is_json:
                try:
                    self._callback(FlaskMessage(request.get_json()))
                    return jsonify({TEXT_STATUS: True}), HTTPStatus.OK
                except Exception as e:
                    return jsonify(
                        {TEXT_STATUS: False, TEXT_MSG: f"{e.__class__.__name__}: {str(e)}"}
                    ), HTTPStatus.BAD_REQUEST
            else:
                return jsonify({TEXT_STATUS: False, TEXT_MSG: f"got a non json data"}), HTTPStatus.BAD_REQUEST

        @self._flask_app.route(TEXT_SLASH_STATUS, methods=[TEXT_GET_CAP])
        @self._flask_app.route(TEXT_SLASH_STATUS_SLASH, methods=[TEXT_GET_CAP])
        async def status():
            return jsonify({TEXT_STATUS: True}), HTTPStatus.OK

    def serve(self):
        webserver = uvicorn.Server(
            config=uvicorn.Config(
                app=WsgiToAsgi(self._flask_app),
                host=self._configuration.flask_ip_port.ip,
                port=self._configuration.flask_ip_port.port,
                use_colors=False,
                log_level="warning"
            )
        )
        update_addr = f"http://{get_ip(self._configuration.flask_ip_port.ip)}:{self._configuration.flask_ip_port.port}{TEXT_SLASH_UPDATE}"
        MetaData.update_addr = update_addr
        logger.info(
            f"Flask is accepting request at: {update_addr}"
        )
        self._event_loop.create_task(webserver.serve())
