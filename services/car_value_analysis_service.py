# car_value_analysis_service.py
import re
import pandas as pd
from copy import deepcopy

from core.price_saving_evaluator          import evaluate as price_eval
from core.mileage_saving_evaluator        import evaluate as mileage_eval
from core.expected_depreciation_evaluator import evaluate as depreciation_eval
from core.market_heat_evaluator           import evaluate as heat_eval
from core.trustworthiness_evaluator       import evaluate as trust_eval
from core.options_evaluator               import evaluate as options_eval
from core.safety_features_evaluator       import evaluate as safety_eval

from db.db              import get_engine
from utils.logger       import Logger
from utils.serialize    import to_native


# ======== 参数变量 ========
table_name               = "dws_rehui_rank_cargurus"                 # 主表
url_field                = "url"                                      # 链接字段
full_key_field           = "full_key"                                 # 车型 key
year_field               = "year"                                     # 年份字段
listing_id_field         = "listing_id"                               # 主键
field_key                = "field"                                    # evaluator 统一字段名键
is_value_field           = "is_value"                                 # evaluator 推荐标记键
msg_field                = "msg"                                      # evaluator 文案键
method_arg_name          = "df"                                       # evaluator 是否需要 df
listing_id_pattern       = r"[#&?]listing=(\d+)"                       # URL 提取 listing_id
query_by_field_tpl       = "SELECT * FROM {table} WHERE {field} = %s"  # 单字段查询

evaluators = [
    price_eval,
    mileage_eval,
    depreciation_eval,
    heat_eval,
    trust_eval,
    options_eval,
    safety_eval
]


# ======== 输出变量 ========
output = {
    "url":            None,     # 页面链接
    "full_key":       None,     # 品牌型号配置 key
    "year":           None,     # 年份
    "highlights":     [],       # 推荐亮点字段列表
    "is_recommended": None,     # 是否推荐
    "summary":        "",       # 汇总推荐理由文本
    "fields":         {}        # 各 evaluator 明细
}


# ======== 工具对象 ========
engine = get_engine()
logger = Logger.get_global_logger()


# ======== 核心方法：通过 URL 获取评估结果 ========
def evaluate_from_url(url: str) -> dict:
    # 提取 listing_id
    match = re.search(listing_id_pattern, url)
    if not match:
        raise ValueError(f"Invalid URL: listing_id not found in {url}")
    listing_id = match.group(1)

    # 查询数据库记录
    query = query_by_field_tpl.format(table=table_name, field=listing_id_field)
    df    = pd.read_sql(query, engine, params=(listing_id,))
    if df.empty:
        raise ValueError(f"No vehicle found with {listing_id_field} = {listing_id}")
    row = df.iloc[0]

    # 日志：基本信息
    logger.info(f"🔍 evaluating listing_id={listing_id} full_key={row[full_key_field]} year={row[year_field]}")

    # 遍历所有评估器
    fields = {}
    for evaluator in evaluators:
        need_df = method_arg_name in evaluator.__code__.co_varnames
        result  = evaluator(df, row) if need_df else evaluator(row)
        fields[result[field_key]] = result

    # 推荐亮点与汇总
    highlights     = [k for k, v in fields.items() if v.get(is_value_field)]
    summary_parts  = [v[msg_field] for v in fields.values() if v.get(is_value_field)]
    is_recommended = len(highlights) > 0
    summary_text   = "；".join(summary_parts) if is_recommended else "暂无明显推荐理由"

    # 构造输出
    result = deepcopy(output)
    result["url"]            = row[url_field]
    result["full_key"]       = row[full_key_field]
    result["year"]           = row[year_field]
    result["fields"]         = fields
    result["highlights"]     = highlights
    result["is_recommended"] = is_recommended
    result["summary"]        = summary_text

    # 日志：完成
    logger.info(f"✅ evaluate done: {result['summary']}")

    # 出口兜底转原生类型
    return to_native(result)
