import pandas as pd
from utils.logger import Logger

# ======== 参数变量 ========
field_name       = "safety_features"
url_field        = "url"
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

# ======== 输出变量 ========
output = {
    "field":      field_name,
    "value":      None,
    "rank":       None,
    "total":      None,
    "is_value":   None,
    "url":        None,
    "msg":        None
}

# ======== 工具对象 ========
logger = Logger.get_global_logger()

def evaluate(row: pd.Series) -> dict:
    features = row[field_name] or []
    matched  = [f for f in features if any(key in f for key in allowed_keywords)]
    count    = len(matched)
    msg      = "高价值安全配置：" + "，".join(matched) if matched else "无高价值安全配置"

    result = output.copy()
    result["value"]     = count
    result["url"]       = row[url_field]
    result["msg"]       = msg
    return result
