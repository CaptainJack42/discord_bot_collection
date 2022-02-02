#!  /usr/bin/env python3.9

import logging
import os

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.environ.get("TEST_API_TOKEN")


class MainClient(commands.Bot):
    def __init__(self, command_prefix="!", case_insensitive_prefix=False, description=None, **options):
        super().__init__(command_prefix, case_insensitive_prefix, description, **options)
        self.logger = self.__setup_logger()

    def __setup_logger(self) -> logging.Logger:
        log_format = "[%(asctime)s] %(levelname)-8s %(name)-12s %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=log_format, filename=("debug.log"))
        file_handler = logging.FileHandler("SoR-Log.log")
        file_handler.setFormatter(logging.Formatter(log_format))
        file_handler.setLevel(logging.DEBUG)
        logger = logging.getLogger("SoR-Logger")
        logger.addHandler(file_handler)
        return logger


if __name__ == "__main__":
    bot = MainClient(command_prefix="!")
    bot.run(API_TOKEN)
