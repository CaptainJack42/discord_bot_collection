import logging

LOGGER = None


def setup_logger() -> logging.Logger:
    log_format = "[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=log_format, filename=("/var/log/discord_bot/API_LOG.log"))
    file_handler = logging.FileHandler("/var/log/discord_bot/Bot_Log.log")
    file_handler.setFormatter(logging.Formatter(log_format))
    file_handler.setLevel(logging.DEBUG)
    global LOGGER
    LOGGER = logging.getLogger("Bot_Logger")
    LOGGER.addHandler(file_handler)
    return LOGGER


def get_logger() -> logging.Logger:
    if LOGGER != None:
        return LOGGER
    else:
        return setup_logger()
