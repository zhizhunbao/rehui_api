import pandas as pd
from utils.logger import Logger

# ======== 参数变量 ========
field_name   = "trustworthiness"
url_field    = "url"
certified    = "certified"
accident_free = "accident_free"
carfax       = "carfax"
as_is        = "as_is"

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
    is_value = (row[certified] or row[accident_free] or row[carfax]) and not row[as_is]
    msg = "车辆具备认证 / 无事故 / 有 CARFAX，可信度高" if is_value else "无认证或存在 AS-IS 风险，建议谨慎"

    result = output.copy()
    result["value"]     = is_value
    result["is_value"]  = is_value
    result["url"]       = row[url_field]
    result["msg"]       = msg
    return result
