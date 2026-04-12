import os
import sys
import logging
import traceback
from datetime import datetime
from colorama import init, Fore, Style
from app.constants import APP_ENV

init(autoreset=True)

# Generate a single log filename per application run
if APP_ENV == "local":
    os.makedirs("logs", exist_ok=True)
    LOG_FILE_PATH = f"logs/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
else:
    LOG_FILE_PATH = None


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    # Catch any unhandled exception globally and write it to the logs
    logging.getLogger("app.crash").error("Uncaught exception",
                                         exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception


class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        color = self.COLORS.get(record.levelno, Fore.WHITE)
        log_fmt = f"[ %(asctime)s ] {Fore.BLUE}%(name)s{Style.RESET_ALL} - {color}%(levelname)s{Style.RESET_ALL} - {color}%(message)s{Style.RESET_ALL}"
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class Logger:
    def __init__(self, name: str = "app"):
        handlers = []

        if APP_ENV == "local":
            if LOG_FILE_PATH:
                file_handler = logging.FileHandler(LOG_FILE_PATH)
                file_handler.setFormatter(logging.Formatter(
                    "[ %(asctime)s ] %(name)s - %(levelname)s - %(message)s"))
                handlers.append(file_handler)
        else:
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setFormatter(ColorFormatter(
                "[ %(asctime)s ] %(name)s - %(levelname)s - %(message)s"))
            handlers.append(stream_handler)

        logging.basicConfig(
            level=logging.INFO,
            handlers=handlers,
            force=True
        )

        for noisy_logger in (
            "httpx",
            "httpcore",
            "hpack",
            "supabase",
        ):
            logging.getLogger(noisy_logger).setLevel(logging.WARNING)

        self.logger = logging.getLogger(name)

    def info(self, message: str, *args, **kwargs):
        self.logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        self.logger.error(message, *args, **kwargs)
