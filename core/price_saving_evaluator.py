import pandas as pd

from utils.logger import Logger


class PriceSavingEvaluator:
    # ======== 成员变量（字段名） ========
    full_key     = "full_key"           # 品牌型号配置
    year         = "year"               # 年份
    price_saving = "price_saving"       # 价格回血字段
    url = "url"

    # ======== 成员变量（判断参数） ========
    min_price_saving = 5000                   # 最低回血金额
    top_k            = 5                      # 排名前 K 内才算值
    min_sample_size  = 5                      # 最小样本量

    # ======== 工具对象 ========
    logger = Logger.get_global_logger()

    @classmethod
    def evaluate(cls, df: pd.DataFrame, row: pd.Series) -> dict:
        # ======== 中间变量 ========
        full_key = row[cls.full_key]
        year     = row[cls.year]
        saving   = row[cls.price_saving]
        url   = row[cls.url]

        group = df[
            (df[cls.full_key] == full_key) &
            (df[cls.year] == year)
            ]

        total = len(group)
        if total < cls.min_sample_size:
            cls.logger.warning(f"⚠️ 样本不足：{full_key} {year} 仅 {total} 条")
            return {
                "field": cls.price_saving,
                "value": saving,
                "rank": None,
                "total": total,
                "is_value": False,
                "url": url,
                "msg": f"样本数不足（{total} 台车），无法判断"
            }

        group_sorted = group.sort_values(cls.price_saving, ascending=False).reset_index(drop=True)
        rank = (group_sorted[cls.price_saving] >= saving).sum()
        is_value = (saving >= cls.min_price_saving) and (rank <= cls.top_k)

        if is_value:
            msg = f"Ranked #{rank} in price saving — significantly above average"
        else:
            msg = f"Price saving is ${saving}, ranked #{rank}, not in top {cls.top_k} or below ${cls.min_price_saving} threshold"

        return {
            "field": cls.price_saving,
            "value": saving,
            "rank": rank,
            "total": total,
            "is_value": is_value,
            "url": url,
            "msg": msg
        }
