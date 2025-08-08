from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from db.db import get_engine
import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

# ======== 参数变量（配置） ========
test_table_name    = "dws_rehui_rank_cargurus"        # 用于测试的表名
test_query_limit   = 5                                 # 查询前 N 条记录
mask_tail_len      = 4                                 # 密码脱敏保留尾部字符数
field_wrap_len     = 100                               # 字段名总长超过此值换行打印

# ======== 参数变量（SQL 语句） ========
sql_ping           = text("SELECT 1")                  # 用于测试连接状态的 SQL
sql_preview        = f"SELECT * FROM {test_table_name} LIMIT {test_query_limit}"  # 查询预览 SQL

# ======== 参数变量（连接信息） ========
engine     = get_engine()                              # SQLAlchemy 引擎
raw_url    = str(engine.url)                           # 原始数据库连接字符串（含密码）
password   = engine.url.password                       # 数据库密码
masked_pw  = "*" * (len(password) - mask_tail_len) + password[-mask_tail_len:]  # 脱敏密码
safe_url   = raw_url.replace(password, masked_pw)      # 脱敏后的数据库 URL

# ======== debug 输出（连接状态） ========
print(f"🔗 当前连接     : {safe_url}")

try:
    with engine.connect() as conn:
        conn.execute(sql_ping)
    print(f"✅ 连接状态     : 成功")
except SQLAlchemyError as e:
    print(f"❌ 连接状态     : 失败（{str(e)[:100]}）")

# ======== debug 输出（查询预览） ========
try:
    df = pd.read_sql(sql_preview, con=engine)
    row_count   = len(df)
    columns_str = ", ".join(df.columns.tolist())

    print(f"✅ 查询表       : {test_table_name}（记录数: {row_count}）")

    if len(columns_str) <= field_wrap_len:
        print(f"📄 字段列表     : {columns_str}")
    else:
        print(f"📄 字段列表     :")
        print("  " + "\n  ".join(df.columns.tolist()))

    print(f"\n📋 前 {test_query_limit} 条数据预览：")
    print(df)

except Exception as e:
    print(f"❌ 查询失败     : {test_table_name}（{str(e)[:100]}）")
