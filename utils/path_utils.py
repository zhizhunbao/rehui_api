import os


def get_project_root():
    """
    返回项目根路径（本文件的上一级目录）
    用于拼接所有配置、数据、日志等路径的根
    """
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def get_abs_path(*relative_path_parts):
    """
    将相对路径部分拼接到项目根路径上，返回绝对路径
    示例：
        get_abs_path('logs') →
            /your/project/logs

        get_abs_path('data', 'raw_data', '20250517') →
            /your/project/data/raw_data/20250517
    """
    return os.path.abspath(os.path.join(get_project_root(), *relative_path_parts))

if __name__ == "__main__":
    from utils.logger import setup_daily_logger
    logger = setup_daily_logger("path_utils")

    root = get_project_root()
    logger.info(f"✅ 项目根目录：{root}")

    test_log_path = get_abs_path("logs", "demo.log")
    logger.info(f"✅ 拼接路径 logs/demo.log：{test_log_path}")
