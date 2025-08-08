import pandas as pd
from utils.logger import Logger


class SafetyFeaturesEvaluator:
    # ======== 参数变量（字段名 & 控制项） ========
    main_field = "safety_features"      # 安全配置字段（列表）
    url        = "url"                  # 页面链接字段

    # ✅ 高价值安全配置关键词白名单
    allowed_keywords = {
        "Automatic Emergency Braking",
        "Lane Departure Warning",
        "Blind Spot Monitoring",
        "Rear Cross Traffic Alert",
        "Adaptive Cruise Control",
        "Parking Sensors",
        "Backup Camera",
        "Curtain Airbags",
        "Frontal Collision Warning",
        "ABS Brakes"
    }

    # ======== 输出变量（评估结果结构） ========
    output = {
        "field":     main_field,        # 当前字段名
        "value":     None,              # 高价值配置个数
        "rank":      None,
        "total":     None,
        "is_value":  None,              # 不做推荐判断
        "url":       None,
        "msg":       None               # 展示安全配置详情
    }

    # ======== 工具对象 ========
    logger = Logger.get_global_logger()

    @classmethod
    def evaluate(cls, row: pd.Series) -> dict:
        # ======== 初始化输出结构 ========
        result = cls.output.copy()

        # ======== 读取原始配置列表（容错） ========
        features = row[cls.main_field] or []

        # ======== 过滤白名单安全配置 ========
        filtered = [feat for feat in features if any(key in feat for key in cls.allowed_keywords)]

        # ======== 拼接展示内容 ========
        count = len(filtered)
        msg   = "Safety Features: " + ", ".join(filtered) if filtered else "No high-value safety features listed"

        # ======== 写入输出字段 ========
        result["value"]     = count
        result["is_value"]  = None
        result["url"]       = row[cls.url]
        result["msg"]       = msg
        return result
