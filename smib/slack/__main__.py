import json
import logging
from pathlib import Path
from pprint import pprint, pp, pformat

import signal
from smib.slack.signal_handlers import sigterm_handler

from simple_websocket_server import WebSocketServer
from slack_bolt import BoltRequest
from slack_bolt.adapter.socket_mode import SocketModeHandler

from smib.slack.logging_injector import inject_logger_to_slack_context
from smib.slack.config import SLACK_APP_TOKEN, SLACK_BOT_TOKEN, APPLICATION_NAME, ROOT_DIRECTORY
from smib.slack.websocket import server as websocket_server
from smib.slack.error import handle_errors
from injectable import Autowired, load_injection_container, autowired, injectable_factory, inject
from smib.slack.plugin.manager import PluginManager
from smib.slack.custom_app import CustomApp

from smib.common.logging_.setup import setup_logging

setup_logging()


@injectable_factory(CustomApp, singleton=True, qualifier="SlackApp")
def create_slack_bolt_app():
    logger: logging.Logger = inject("logger")
    app: CustomApp = CustomApp(token=SLACK_BOT_TOKEN,
                               raise_error_for_unhandled_request=True,
                               request_verification_enabled=False,
                               token_verification_enabled=False,
                               process_before_response=True,
                               ignoring_self_events_enabled=True,
                               ssl_check_enabled=False,
                               name=APPLICATION_NAME,
                               )
    logger.info(f"Created SlackApp: {APPLICATION_NAME}")
    app.error(handle_errors)
    app.middleware(inject_logger_to_slack_context)
    logger.debug(f"Registered SlackApp error handler: {handle_errors}")
    return app


@autowired
def create_slack_socket_mode_handler(app: Autowired("SlackApp")):
    logger: logging.Logger = inject("logger")
    handler = SocketModeHandler(app,
                                app_token=SLACK_APP_TOKEN,
                                trace_enabled=True,
                                all_message_trace_enabled=True,
                                ping_pong_trace_enabled=True,
                                ping_interval=30
                                )

    @handler.client.on_message_listeners.append
    def _listener(raw_message):
        json_message: dict = json.loads(raw_message)
        if json_message.get('type') == "hello":
            app.num_connections = json_message["num_connections"]
            logger.info(f"{app.num_connections = }")

    logger.info(f"Created SocketModeHandler")
    return handler


def main():
    load_injection_container(ROOT_DIRECTORY / "common")
    load_injection_container(ROOT_DIRECTORY / "slack")

    signal.signal(signal.SIGTERM, sigterm_handler)

    logger: logging.Logger = inject("logger")

    plugin_manager = inject(PluginManager)
    plugin_manager.load_all_plugins()

    slack_socket_mode_handler = create_slack_socket_mode_handler()

    ws_server_thread = websocket_server.start_threaded_server()
    ws_server = inject(WebSocketServer)

    try:
        logger.info(f"Starting SocketModeHandler")
        slack_socket_mode_handler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info(f"Stopping {APPLICATION_NAME}")
    except Exception as e:
        logger.exception(e)
    finally:
        logger.info(f"Stopping WebSocketServer")
        ws_server.close()
        ws_server_thread.join(timeout=5)
        logger.info(f"Stopping SocketModeHandler Client")
        slack_socket_mode_handler.client.close()
        logger.info(f"Stopping SocketModeHandler")
        slack_socket_mode_handler.close()
        logger.info("Goodbye!")


if __name__ == '__main__':
    main()
