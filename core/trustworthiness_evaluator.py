import pandas as pd
from utils.logger import Logger


class TrustworthinessEvaluator:
    # ======== 参数变量（字段名 & 判断逻辑） ========
    main_field     = "trustworthiness"
    certified      = "certified"
    accident_free  = "accident_free"
    carfax         = "carfax"
    as_is          = "as_is"
    url            = "url"

    # ======== 输出变量（评估结果结构） ========
    output = {
        "field":     main_field,              # 虚拟字段名
        "value":     None,                    # True / False
        "rank":      None,                    # 不适用
        "total":     None,                    # 不适用
        "is_value":  None,                    # 是否值得信任
        "url":       None,                    # 页面链接
        "msg":       None                     # 文案说明
    }

    # ======== 工具对象 ========
    logger = Logger.get_global_logger()

    @classmethod
    def evaluate(cls, row: pd.Series) -> dict:
        result = cls.output.copy()

        certified     = row[cls.certified]
        accident_free = row[cls.accident_free]
        carfax        = row[cls.carfax]
        as_is         = row[cls.as_is]
        url           = row[cls.url]

        is_value = (certified or accident_free or carfax) and not as_is
        msg = (
            "Vehicle is certified / accident-free / has CARFAX — trustworthy"
            if is_value else
            "Missing certification or has AS-IS risk — not trustworthy"
        )

        result["value"]     = is_value
        result["is_value"]  = is_value
        result["url"]       = url
        result["msg"]       = msg
        return result
