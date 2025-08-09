import pandas as pd
from utils.logger import Logger

# ======== 参数变量 ========
field_full_key      = "full_key"              # 品牌+型号+配置（用于分组）
field_year          = "year"                  # 年份（用于分组）
field_url           = "url"                   # 车辆详情页链接
field_main          = "heat_rank"             # 本命字段：热度排名（越小越热）

top_k               = 5                       # 热度前 top_k 排名才推荐
min_sample_size     = 5                       # 最小样本数，小于此值不做判断

# ======== 输出变量 ========
output = {
    "field":        field_main,               # 当前评估字段名
    "value":        None,                     # 当前热度排名
    "rank":         None,                     # 在同组内的排名
    "sample_size":  None,                     # 同组样本数
    "is_value":     None,                     # 是否值得推荐
    "url":          None,                     # 车辆链接
    "msg":          None                      # 分析说明
}

# ======== 工具对象 ========
logger = Logger.get_global_logger()


def evaluate(df: pd.DataFrame, row: pd.Series) -> dict:
    # ======== 中间变量计算 ========
    group        = df[(df[field_full_key] == row[field_full_key]) & (df[field_year] == row[field_year])]
    value        = row[field_main]
    sample_size  = len(group)

    if sample_size < min_sample_size:
        rank     = None
        is_value = False
        msg      = f"样本数不足（{sample_size} 台），无法判断"
        logger.warning(f"⚠️ 样本不足：{row[field_full_key]} {row[field_year]} → {sample_size}")
    else:
        # ✅ 排名越小越热门（值越小越推荐）
        rank     = (group.sort_values(field_main, ascending=True)[field_main] <= value).sum()
        is_value = rank <= top_k
        msg      = (
            f"热度排名第 {rank}，进入前 {top_k}，值得推荐"
            if is_value else
            f"热度排名为 {value}，排第 {rank}，未进前 {top_k}"
        )

    # ======== 输出结构赋值 ========
    result = output.copy()
    result["value"]        = value
    result["rank"]         = rank
    result["sample_size"]  = sample_size
    result["is_value"]     = is_value
    result["url"]          = row[field_url]
    result["msg"]          = msg
    return result
