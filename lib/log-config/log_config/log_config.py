from typing import Literal
from logging.config import dictConfig

def set_logging(log_level: Literal["ERROR", "WARNING", "INFO", "DEBUG"]):
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,

        "formatters": {
            "colored": {
                "()": "colorlog.ColoredFormatter",
                "format": "[%(asctime)s] %(log_color)s%(levelname)s%(reset)s:"
                          " (%(module)s) %(message)s",
                "log_colors": {
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "purple",
                },
            },
        },

        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "colored",
            },
        },

        "root": {
            "level": log_level,
            "handlers": ["console"],
        },
    }
    dictConfig(LOGGING_CONFIG)