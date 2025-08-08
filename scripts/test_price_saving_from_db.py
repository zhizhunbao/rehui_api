import pandas as pd

from core.price_saving_evaluator import PriceSavingEvaluator
from db.db import get_engine
from utils.logger import Logger
from utils import url_utils


def test_price_saving_from_db():
    # ======== 工具对象 ========
    engine = get_engine()
    logger = Logger.get_global_logger()

    # ======== 目标参数 ========
    table_name        = "dws_rehui_rank_cargurus"
    target_url        = "https://www.cargurus.ca/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?zip=M9C&distance=250&entitySelectingHelper.selectedEntity=m6#listing=419019859/HIGHLIGHT/DEFAULT"
    field_listing_id  = "listing_id"

    listing_id = url_utils.extract_listing_id(target_url)

    # ======== SQL 查询 ========
    sql_row  = f"SELECT * FROM {table_name} WHERE {field_listing_id} = '{listing_id}'"
    row      = pd.read_sql(sql_row, engine)
    if row.empty:
        logger.error("❌ 未找到对应车辆，请检查 URL 是否正确")
        return

    # ======== 提取车型参数 ========
    target_row = row.iloc[0]
    full_key   = target_row["full_key"]
    year       = target_row["year"]

    # ======== 查询同车型样本 ========
    sql_group = f"SELECT * FROM {table_name} WHERE full_key = '{full_key}' AND year = {year}"
    group     = pd.read_sql(sql_group, engine)

    # ======== 执行打分 ========
    result = PriceSavingEvaluator.evaluate(group, target_row)

    # ======== 打印结果 ========
    print("🎯 PriceSavingEvaluator 实测输出：")
    for k, v in result.items():
        print(f"{k:<10}: {v}")

if __name__ == "__main__":
    test_price_saving_from_db()
