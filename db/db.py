import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# ======== 加载 .env 文件配置 ========
load_dotenv()

# ======== 模式切换开关 ========
LOCAL_MODE = os.getenv("LOCAL_MODE", "false").lower() == "true"  # 是否使用本地数据库（true）还是云端 Render（false）

# ======== 本地数据库配置（来自 .env） ========
LOCAL_DB_USER     = os.getenv("LOCAL_DB_USER")      # 本地数据库用户名
LOCAL_DB_PASSWORD = os.getenv("LOCAL_DB_PASSWORD")  # 本地数据库密码
LOCAL_DB_HOST     = os.getenv("LOCAL_DB_HOST")      # 本地数据库主机（如 localhost）
LOCAL_DB_PORT     = os.getenv("LOCAL_DB_PORT")      # 本地数据库端口（如 5432）
LOCAL_DB_NAME     = os.getenv("LOCAL_DB_NAME")      # 本地数据库名称

# ======== Render 云数据库配置（来自 .env） ========
RENDER_DB_USER     = os.getenv("RENDER_DB_USER")      # Render 云端数据库用户名
RENDER_DB_PASSWORD = os.getenv("RENDER_DB_PASSWORD")  # Render 云端数据库密码
RENDER_DB_HOST     = os.getenv("RENDER_DB_HOST")      # Render 云端数据库主机地址
RENDER_DB_PORT     = os.getenv("RENDER_DB_PORT")      # Render 云端数据库端口
RENDER_DB_NAME     = os.getenv("RENDER_DB_NAME")      # Render 云端数据库名称

# ======== 固定连接参数（内部用） ========
DB_DRIVER_PREFIX   = "postgresql+psycopg2"   # 数据库驱动前缀（SQLAlchemy 使用 psycopg2）
DB_ECHO            = False                   # 是否打印 SQL（建议关闭）
DB_POOL_PRE_PING   = True                    # 检查连接池连接是否存活（防止失效连接报错）

# ======== 获取 SQLAlchemy 引擎实例 ========
def get_engine():
    # ======== 参数选择（按当前运行环境） ========
    db_user = LOCAL_DB_USER     if LOCAL_MODE else RENDER_DB_USER
    db_pass = LOCAL_DB_PASSWORD if LOCAL_MODE else RENDER_DB_PASSWORD
    db_host = LOCAL_DB_HOST     if LOCAL_MODE else RENDER_DB_HOST
    db_port = LOCAL_DB_PORT     if LOCAL_MODE else RENDER_DB_PORT
    db_name = LOCAL_DB_NAME     if LOCAL_MODE else RENDER_DB_NAME

    # ======== 参数完整性校验 ========
    if not all([db_user, db_pass, db_host, db_port, db_name]):
        raise ValueError("❌ 缺少数据库连接信息，请检查 .env 文件")

    # ======== 拼接连接字符串 & 创建引擎 ========
    db_url  = f"{DB_DRIVER_PREFIX}://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    engine  = create_engine(db_url, echo=DB_ECHO, pool_pre_ping=DB_POOL_PRE_PING)

    return engine
