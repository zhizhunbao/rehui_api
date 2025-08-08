import pandas as pd
from utils.logger import Logger

class PriceSavingEvaluator:
    # ======== 参数变量（字段名 & 判断逻辑） ========
    full_key         = "full_key"            # 品牌+型号+配置（用于分组）
    year             = "year"                # 车型年份（用于分组）
    main_field       = "price_saving"        # 回血字段名（作为打分核心）
    url              = "url"                 # 车辆页面链接（用于展示）

    top_k            = 5                     # 回血金额需排名前 top_k 才算值
    min_sample_size  = 5                     # 最小样本数量（小于该值不评估）

    # ======== 输出变量（评估结果结构） ========
    output = {
        "field":     main_field,           # 当前评估字段
        "value":     None,                   # 当前值（如 price_saving 数值）
        "rank":      None,                   # 在同组中的排名（越靠前越好）
        "total":     None,                   # 同组样本数量（如 full_key+year）
        "is_value":  None,                   # 是否值得推荐
        "url":       None,                   # 当前车辆链接
        "msg":       None                    # 解释文字（用户可读）
    }

    # ======== 工具对象 ========
    logger = Logger.get_global_logger()

    @classmethod
    def evaluate(cls, df: pd.DataFrame, row: pd.Series) -> dict:
        group = df[(df[cls.full_key] == row[cls.full_key]) & (df[cls.year] == row[cls.year])]
        result = cls.output.copy()

        value     = row[cls.main_field]
        url       = row[cls.url]
        total     = len(group)

        if total < cls.min_sample_size:
            cls.logger.warning(f"⚠️ 样本不足：{row[cls.full_key]} {row[cls.year]} 仅 {total} 条")
            rank     = None
            is_value = False
            msg      = f"样本数不足（{total} 台车），无法判断"
        else:
            rank = (group.sort_values(cls.main_field, ascending=False)[cls.main_field] >= value).sum()
            is_value = rank <= cls.top_k
            msg = (
                f"Ranked #{rank} in price saving — top {cls.top_k} value pick"
                if is_value else
                f"Price saving is ${value}, ranked #{rank}, not in top {cls.top_k}"
            )

        result["value"]     = value
        result["rank"]      = rank
        result["total"]     = total
        result["is_value"]  = is_value
        result["url"]       = url
        result["msg"]       = msg

        return result