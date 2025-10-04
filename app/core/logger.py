import logging
import sys
from functools import lru_cache

class Logger:
    def __init__(self):
        self._logger = logging.getLogger("finbot")
        self._logger.setLevel(logging.INFO)

        if not self._logger.handlers:  # tránh add handler 2 lần khi reload
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

    @property
    def instance(self) -> logging.Logger:
        return self._logger


@lru_cache
def get_logger() -> logging.Logger:
    """Singleton logger, đảm bảo chỉ init 1 lần"""
    return Logger().instance
