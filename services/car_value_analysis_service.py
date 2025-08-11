# services/car_value_analysis_service.py
import re
import pandas as pd

from db.db           import get_engine
from utils.logger    import Logger
from utils.serialize import to_native
from core.car_value_evaluator import evaluate as build_result  # 你刚写的 evaluator（中文推荐理由）

# ======== 参数变量 ========
TABLE_NAME         = "dws_rehui_rank_cargurus"
FIELD_LISTING_ID   = "listing_id"
FIELD_FULL_KEY     = "full_key"
FIELD_YEAR         = "year"
FIELD_URL          = "url"
LISTING_ID_PATTERN = r"[#&?]listing=(\d+)"

# ======== 工具对象 ========
engine = get_engine()
logger = Logger.get_global_logger()

# ======== 内部：查询工具 ========
def _fetch_row_by_listing_id(listing_id: str) -> pd.Series:
    sql = f"""
        SELECT *
        FROM {TABLE_NAME}
        WHERE {FIELD_LISTING_ID} = %s
        LIMIT 1
    """
    df = pd.read_sql(sql, engine, params=(listing_id,))
    if df.empty:
        raise ValueError(f"No vehicle found with {FIELD_LISTING_ID} = {listing_id}")
    return df.iloc[0]

def _fetch_cohort(full_key: str, year: int) -> pd.DataFrame:
    sql = f"""
        SELECT *
        FROM {TABLE_NAME}
        WHERE {FIELD_FULL_KEY} = %s
          AND {FIELD_YEAR} = %s
    """
    return pd.read_sql(sql, engine, params=(full_key, int(year)))

# ======== 对外：通过 URL 评估（只输出一个 JSON） ========
def evaluate_from_url(url: str) -> dict:
    # 1) 解析 listing_id
    m = re.search(LISTING_ID_PATTERN, url)
    if not m:
        raise ValueError(f"Invalid URL: listing_id not found in {url}")
    listing_id = m.group(1)

    # 2) 查单条 row
    row = _fetch_row_by_listing_id(listing_id)

    # 3) 查 cohort df（同 full_key + year）
    df = _fetch_cohort(row[FIELD_FULL_KEY], int(row[FIELD_YEAR]))

    logger.info(
        f"🔍 evaluating listing_id={listing_id} "
        f"full_key={row[FIELD_FULL_KEY]} year={row[FIELD_YEAR]} (cohort_size={len(df)})"
    )

    # 4) 交给 evaluator 产出唯一 JSON
    result = build_result(df, row)

    logger.info(f"✅ evaluate done: {result.get('summary')}")
    return to_native(result)

# ======== 可选：直接用 listing_id 评估（方便内部调用/单测） ========
def evaluate_by_listing_id(listing_id: str) -> dict:
    row = _fetch_row_by_listing_id(listing_id)
    df  = _fetch_cohort(row[FIELD_FULL_KEY], int(row[FIELD_YEAR]))
    result = build_result(df, row)
    logger.info(f"✅ evaluate_by_listing_id done: {result.get('summary')}")
    return to_native(result)
