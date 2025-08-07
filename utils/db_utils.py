from collections import OrderedDict
from logging import Logger
from typing import List, Optional

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError


# ========= 🌐 初始化 =========
def get_sqlalchemy_engine(host: str, port: int, db: str, user: str, password: str) -> Engine:
    """
    创建 SQLAlchemy Engine 实例（PostgreSQL）
    示例连接串：postgresql+psycopg2://user:password@host:port/db
    """
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    engine = create_engine(url, echo=False, pool_pre_ping=True)
    return engine

# ========= 🧾 通用 SQL 执行 =========
def run_query_raw(engine: Engine, sql: str, params: Optional[dict], auto_commit: bool = True) -> Optional[List[tuple]]:
    """
    通用 SQL 执行函数，支持 SELECT / INSERT / UPDATE / DELETE / DDL。

    参数说明：
    - engine: SQLAlchemy 数据库引擎
    - sql: 要执行的 SQL 语句（支持占位符，如 :param）
    - params: 参数字典（用于绑定变量），可选
    - auto_commit: 非查询语句是否自动提交（默认 True）

    返回值：
    - 对于 SELECT 语句，返回 List[tuple] 结果
    - 对于其他语句，返回 None
    """
    with engine.connect() as conn:
        trans = conn.begin() if auto_commit else None
        try:
            result = conn.execute(sql, params or {})
            if trans:
                trans.commit()
            if result.returns_rows:
                return result.fetchall()
            return None
        except Exception as e:
            if trans:
                trans.rollback()
            raise e


def run_query_df(engine: Engine, sql: str, params: dict = None, logger: Logger = None) -> pd.DataFrame:
    try:
        return pd.read_sql(sql, con=engine, params=params)
    except Exception as e:
        if logger:
            logger.error(f"❌ 查询失败: {e}")
        else:
            print(f"❌ 查询失败: {e}")  # 没有 logger 时 fallback 到标准输出
        return pd.DataFrame()



# ========= 📄 表读写 =========
def read_table_as_dataframe(engine, table_name: str, logger: Logger) -> pd.DataFrame:
    """
    读取指定表为 Pandas DataFrame（整表读取）

    参数：
        engine: SQLAlchemy Engine 对象
        table_name: 要读取的表名（支持 schema.table）

    返回：
        pd.DataFrame：包含表中所有数据，若出错返回空 DataFrame
    """
    try:
        df = pd.read_sql(f"SELECT * FROM {table_name}", con=engine)
        if logger:
            logger.info(f"✅ 成功读取表：{table_name}，共 {len(df)} 条记录")
        return df
    except Exception as e:
        if logger:
            logger.info(f"❌ 读取失败：{table_name}，错误：{e}")
        return pd.DataFrame()


from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
from sqlalchemy.engine import Engine
from typing import List
from logging import Logger

def insert_batch(
        engine: Engine,
        table_name: str,
        records: List[dict],
        fields: List[str],
        batch_size: int = 100,
        logger: Logger = None
):
    """
    批量插入数据到 PostgreSQL 表中

    参数：
        engine: SQLAlchemy Engine 对象
        table_name: 目标表名（如 public.my_table）
        records: 字典列表，每个元素是一行数据
        fields: 插入字段名列表，需与表结构匹配
        batch_size: 每批插入的数据量，默认 100
    """
    if not records:
        if logger:
            logger.info(f"⚠️ 无可插入数据：{table_name}")
        return

    try:
        df = pd.DataFrame(records)[fields]

        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i + batch_size]
            batch.to_sql(table_name, engine, if_exists='append', index=False, method='multi')
            if logger:
                logger.info(f"✅ 插入成功：{table_name} 第 {i} ~ {i + len(batch) - 1} 条")

        if logger:
            logger.info(f"✅ 成功插入 {len(df):,} 条记录 → {table_name}")

    except SQLAlchemyError as e:
        if logger:
            logger.error(f"❌ 插入失败：{table_name}，异常：{str(e)[:300]}...")

# ========= 🧱 表结构管理 =========
def create_table_if_not_exists(engine, table_name: str, schema: OrderedDict, logger: Logger):
    """
    按 schema 定义创建 PostgreSQL 表（若不存在）
    """
    columns_def = ",\n  ".join([f"{col} {dtype}" for col, dtype in schema.items()])
    create_sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
      {columns_def}
    );
    """
    with engine.connect() as conn:
        conn.execute(text(create_sql))
        conn.commit()
        if logger:
            logger.info(f"✅ 表已确认存在：{table_name}")


def drop_table_if_exists(engine, table_name: str, logger):
    sql = f"DROP TABLE IF EXISTS {table_name};"
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
        if logger:
            logger.info(f"🗑️ 表已删除（如存在）：{table_name}")

def truncate_if_exists(engine, table_name: str, logger: Logger):
    """
    清空表内容（如果存在），并重置自增序列（RESTART IDENTITY）
    """
    sql = f"TRUNCATE TABLE {table_name} RESTART IDENTITY;"
    with engine.connect() as conn:
        conn.execute(sql)
        conn.commit()
        if logger:
            logger.info(f"🧹 表已清空并重置序列：{table_name}")


