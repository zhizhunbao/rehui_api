import pandas as pd
from utils.logger import Logger


class MarketHeatEvaluator:
    # ======== 参数变量（字段名 & 判断逻辑） ========
    full_key        = "full_key"            # 品牌+型号+配置（用于分组）
    year            = "year"                # 车型年份（用于分组）
    url             = "url"                 # 页面链接字段
    main_field      = "heat_rank"           # 本命字段：热度排名（越小越热）

    top_k           = 5                     # 排名前 top_k 才算热门
    min_sample_size = 5                     # 最小样本数量

    # ======== 输出变量（评估结果结构） ========
    output = {
        "field":     main_field,            # 当前评估字段
        "value":     None,                  # 当前值（热度排名）
        "rank":      None,                  # 在同组中排名
        "total":     None,                  # 样本总数
        "is_value":  None,                  # 是否值得推荐
        "url":       None,                  # 车辆链接
        "msg":       None                   # 分析说明
    }

    # ======== 工具对象 ========
    logger = Logger.get_global_logger()

    @classmethod
    def evaluate(cls, df: pd.DataFrame, row: pd.Series) -> dict:
        group = df[(df[cls.full_key] == row[cls.full_key]) & (df[cls.year] == row[cls.year])]
        result = cls.output.copy()

        value = row[cls.main_field]
        url   = row[cls.url]
        total = len(group)

        if total < cls.min_sample_size:
            cls.logger.warning(f"⚠️ 样本不足：{row[cls.full_key]} {row[cls.year]} 仅 {total} 条")
            rank     = None
            is_value = False
            msg      = f"样本数不足（{total} 台车），无法判断"
        else:
            # ✅ 排名越小越热门，ascending=True
            rank = (group.sort_values(cls.main_field, ascending=True)[cls.main_field] <= value).sum()
            is_value = rank <= cls.top_k
            msg = (
                f"Ranked #{rank} in market heat — top {cls.top_k} hot pick"
                if is_value else
                f"Market heat rank is {value}, ranked #{rank}, not in top {cls.top_k} (lower is better)"
            )

        result["value"]     = value
        result["rank"]      = rank
        result["total"]     = total
        result["is_value"]  = is_value
        result["url"]       = url
        result["msg"]       = msg
        return result
