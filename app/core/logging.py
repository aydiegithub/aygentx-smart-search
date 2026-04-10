import sys
import logging


class Logger:
    def __init__(self, name: str = "app"):
        logging.basicConfig(
            level=logging.INFO,
            format="[ %(asctime)s ] %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout)
            ],
        )

        for noisy_logger in (
            "httpx",
            "httpcore",
            "hpack",
            "supabase",
        ):
            logging.getLogger(noisy_logger).setLevel(logging.WARNING)

        self.logger = logging.getLogger(name)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)