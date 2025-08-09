import pandas as pd
from utils.logger import Logger

# ======== 参数变量 ========
field_name       = "options"     # 配置字段（列表）
url_field        = "url"         # 页面链接字段
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

# ======== 输出变量 ========
output = {
    "field":     field_name,
    "value":     None,
    "rank":      None,
    "total":     None,
    "is_value":  None,
    "url":       None,
    "msg":       None
}

# ======== 工具对象 ========
logger = Logger.get_global_logger()

def evaluate(row: pd.Series) -> dict:
    options  = row[field_name] or []
    filtered = [opt for opt in options if any(key in opt for key in allowed_keywords)]
    count    = len(filtered)
    msg      = "高价值配置：" + "，".join(filtered) if filtered else "无高价值配置"

    result = output.copy()
    result["value"]     = count
    result["is_value"]  = None
    result["url"]       = row[url_field]
    result["msg"]       = msg
    return result
