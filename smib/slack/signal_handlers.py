import logging

from injectable import inject


def sigterm_handler(signum, frame):
    logger: logging.Logger = inject("logger")

    logger.info("Received shutdown signal")
    logger.debug(f'Signal handler called with signal, {signum}')

    raise SystemExit('Exiting...')
