import logging
import os
from datetime import datetime

from utils.path_utils import get_abs_path


class Logger:
    _global_logger = None  # 单例缓存

    def __init__(self, logger_name: str = None, date_str: str = None, log_dir: str = 'logs'):
        # ======== 参数变量 ========
        self.logger_name = logger_name or __name__
        self.date_str    = date_str or datetime.now().strftime('%Y%m%d')
        self.log_dir     = log_dir

        # ======== 中间变量 ========
        self.log_file = get_abs_path(self.log_dir, f"{self.logger_name}_{self.date_str}.log")
        self.logger   = self._setup_logger()

    def _setup_logger(self):
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        logger = logging.getLogger(self.logger_name)
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            formatter = logging.Formatter(
                fmt='[%(asctime)s] %(levelname)s | %(filename)s | %(funcName)s | %(message)s',
                datefmt='%H:%M:%S'
            )

            fh = logging.FileHandler(self.log_file, encoding='utf-8')
            fh.setFormatter(formatter)
            logger.addHandler(fh)

            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            logger.addHandler(ch)

        return logger

    def get_logger(self):
        return self.logger

    @staticmethod
    def get_global_logger():
        if Logger._global_logger is None:
            Logger._global_logger = Logger().get_logger()
        return Logger._global_logger
