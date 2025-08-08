import pandas as pd
from utils.logger import Logger


class OptionsEvaluator:
    # ======== 参数变量（字段名 & 控制项） ========
    main_field = "options"       # 配置字段（列表类型）
    url        = "url"           # 页面链接字段

    # ✅ 配置项关键词白名单：仅保留这些高价值配置用于展示
    allowed_keywords = {
        "Leather Seats",
        "Navigation",
        "Sunroof",
        "Moonroof",
        "Heated Seats",
        "Heated Steering Wheel",
        "Remote Start",
        "Third Row Seating",
        "Premium Sound System",
        "Adaptive Cruise Control",
        "Ventilated Seats",
        "Heads-Up Display"
    }

    # ======== 输出变量（评估结果结构） ========
    output = {
        "field":     main_field,       # 当前字段名
        "value":     None,             # 配置数量（过滤后）
        "rank":      None,
        "total":     None,
        "is_value":  None,             # 不做推荐，仅展示
        "url":       None,             # 页面链接
        "msg":       None              # 展示配置项文本
    }

    # ======== 工具对象 ========
    logger = Logger.get_global_logger()

    @classmethod
    def evaluate(cls, df: pd.DataFrame, row: pd.Series) -> dict:
        # ======== 初始化输出结构 ========
        result = cls.output.copy()

        # ======== 读取原始配置列表（容错） ========
        options = row[cls.main_field] or []

        # ======== 过滤白名单关键词配置项 ========
        filtered = [opt for opt in options if any(key in opt for key in cls.allowed_keywords)]

        # ======== 输出内容拼接 ========
        count = len(filtered)
        msg   = "Options: " + ", ".join(filtered) if filtered else "No high-value options listed"

        # ======== 写入输出字段 ========
        result["value"]     = count
        result["is_value"]  = None
        result["url"]       = row[cls.url]
        result["msg"]       = msg
        return result
