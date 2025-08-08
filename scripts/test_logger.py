from utils.logger import Logger


def test_logger():
    # ======== 参数变量 ========
    logger           = Logger.get_global_logger()            # 全局日志器实例
    message_info     = "✅ Logger 模块已成功启动"             # INFO 测试信息
    message_warning  = "⚠️ 这是一个警告信息"                  # WARNING 测试信息
    message_error    = "❌ 这是一个错误信息"                  # ERROR 测试信息

    # ======== 日志输出 ========
    logger.info(message_info)
    logger.warning(message_warning)
    logger.error(message_error)


if __name__ == "__main__":
    test_logger()
