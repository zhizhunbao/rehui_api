import pandas as pd
from utils.logger import Logger

# ======== 参数变量 ========
field_name       = "price_saving"    # 回血字段名
group_key        = "full_key"        # 分组字段：品牌+型号+配置
year_field       = "year"            # 分组字段：年份
url_field        = "url"             # 页面链接字段
top_k            = 5                 # 排名前 top_k 才推荐
min_sample_size  = 5                 # 最小样本数量要求

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

def evaluate(df: pd.DataFrame, row: pd.Series) -> dict:
    group     = df[(df[group_key] == row[group_key]) & (df[year_field] == row[year_field])]
    result    = output.copy()
    value     = row[field_name]
    url       = row[url_field]
    total     = len(group)

    if total < min_sample_size:
        logger.warning(f"⚠️ 样本不足：{row[group_key]} {row[year_field]} 仅 {total} 条")
        rank     = None
        is_value = False
        msg      = f"样本数不足（{total} 台车），无法判断"
    else:
        rank     = (group.sort_values(field_name, ascending=False)[field_name] >= value).sum()
        is_value = rank <= top_k
        msg      = f"价格回血排第 {rank} 名，进入前 {top_k}，值得推荐" if is_value else f"价格回血为 ${value}，排第 {rank} 名，未进前 {top_k}"

    result["value"]     = value
    result["rank"]      = rank
    result["total"]     = total
    result["is_value"]  = is_value
    result["url"]       = url
    result["msg"]       = msg
    return result
