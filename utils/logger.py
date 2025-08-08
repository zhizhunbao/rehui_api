import logging
import os
from datetime import datetime
from utils.path_utils import get_abs_path


class Logger:
    _global_logger = None  # 全局日志单例缓存，避免重复创建

    def __init__(self):
        # ======== 默认值定义 ========
        logger_name = "rehui_api"                                     # 默认日志器名称
        date_str    = datetime.now().strftime('%Y%m%d')               # 日志日期字符串（格式：20250807）
        log_dir     = "logs"                                          # 日志输出目录

        # ======== 参数变量 ========
        self.logger_name = logger_name                                # 日志器名称
        self.date_str    = date_str                                   # 当前日期字符串
        self.log_dir     = log_dir                                    # 日志目录

        # ======== 常量定义 ========
        self.log_suffix   = ".log"                                    # 日志文件后缀
        self.log_level    = logging.INFO                              # 日志级别：INFO
        self.time_format  = "%H:%M:%S"                                # 日志时间格式（仅时分秒）
        self.log_format   = "[%(asctime)s] %(levelname)s | %(filename)s | %(funcName)s | %(message)s"

        # ======== 创建目录（确保日志目录存在） ========
        abs_log_dir = get_abs_path(self.log_dir)
        if not os.path.exists(abs_log_dir):
            os.makedirs(abs_log_dir)

        # ======== 中间变量 ========
        self.log_filename   = f"{self.logger_name}_{self.date_str}{self.log_suffix}"  # 日志文件名
        self.log_file_path  = get_abs_path(self.log_dir, self.log_filename)           # 日志完整路径
        self.logger         = self._setup_logger()                                                    # 实际 logger 实例

    def _setup_logger(self):
        # ======== 参数变量 ========
        log_path     = self.log_file_path                        # 日志文件路径
        log_dir      = os.path.dirname(log_path)                 # 日志目录路径
        logger_name  = self.logger_name                          # 日志器名称
        level        = self.log_level                            # 日志级别
        fmt          = self.log_format                           # 日志内容格式
        time_fmt     = self.time_format                          # 时间显示格式

        # ======== 中间变量 ========
        logger         = logging.getLogger(logger_name)          # 获取 logger 实例
        formatter      = logging.Formatter(fmt=fmt, datefmt=time_fmt)      # 格式器
        file_handler   = logging.FileHandler(log_path, encoding="utf-8")   # 文件输出 handler
        stream_handler = logging.StreamHandler()                           # 控制台输出 handler

        # ======== 日志器配置 ========
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        logger.setLevel(level)
        if not logger.handlers:
            file_handler.setFormatter(formatter)
            stream_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            logger.addHandler(stream_handler)

        return logger

    def get_logger(self):
        return self.logger

    @staticmethod
    def get_global_logger():
        """
        获取全局唯一 logger 实例，避免多次重复创建
        """
        if Logger._global_logger is None:
            Logger._global_logger = Logger().get_logger()
        return Logger._global_logger