# main_api.py
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl

from utils.logger import Logger
from utils.path_utils import get_abs_path
from services.car_value_analysis_service import (
    evaluate_from_url,
    evaluate_by_listing_id,
)

import os
import uvicorn

# ===== 配置（全小写） =====
app_title   = "rehui api"
app_version = "v1"
host        = "0.0.0.0"
port        = 8000
reload_flag = True
watch_dirs  = ["api", "services", "core", "utils"]  # 想监听谁就写谁

logger = Logger.get_global_logger()

# ===== 工具函数：预测热重载模式（基于是否安装 watchfiles）=====
def predict_reload_mode() -> str:
    try:
        import watchfiles  # noqa: F401
        return "WatchFilesReload"
    except Exception:
        return "StatReload"

# ===== 生命周期（Lifespan 版）=====
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动完成后确认（用与预测相同的判定：是否安装 watchfiles）
    try:
        import watchfiles  # noqa: F401
        actual = "WatchFilesReload"
    except Exception:
        actual = "StatReload"

    logger.info("🚀 服务启动成功")
    logger.info(f"🚀 当前热重载模式: {actual}")
    yield
    logger.info("🛑 服务已关闭")

# ===== 应用 =====
app = FastAPI(title=app_title, version=app_version, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# ===== 健康检查 =====
@app.get("/healthz")
def healthz() -> Dict[str, str]:
    return {"status": "ok"}

# ===== 请求模型 =====
class evaluate_req(BaseModel):
    url: HttpUrl

# ===== 接口（内联，省去 controller 层）=====
@app.post("/api/evaluate")
async def api_evaluate(req: evaluate_req) -> Dict[str, Any]:
    logger.info(f"🔍 接收到评估请求: {req.url}")
    try:
        return evaluate_from_url(str(req.url))
    except ValueError as e:
        logger.warning(f"⚠️ 参数错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"💥 服务异常: {e}")
        raise HTTPException(status_code=500, detail="internal server error")

@app.get("/api/evaluate/{listing_id}")
async def api_evaluate_by_id(listing_id: str) -> Dict[str, Any]:
    logger.info(f"🔍 按 listing_id 评估: {listing_id}")
    try:
        return evaluate_by_listing_id(listing_id)
    except ValueError as e:
        logger.warning(f"⚠️ 参数错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"💥 服务异常: {e}")
        raise HTTPException(status_code=500, detail="internal server error")

# ===== 开发启动（WatchFilesReload + 启动信息打印，纯 Lifespan 版）=====
if __name__ == "__main__":
    # 只监听必要源码目录
    abs_dirs = [get_abs_path(d) for d in watch_dirs if os.path.isdir(get_abs_path(d))]
    if not abs_dirs:
        abs_dirs = [get_abs_path(".")]

    # 启动前打印“预计热重载模式”
    logger.info(f"🚀 预计热重载模式: {predict_reload_mode()}")

    # 打印启动信息
    logger.info(f"🔧 热加载监听：{abs_dirs}")
    logger.info("📄 swagger: http://localhost:8000/docs")
    logger.info("📄 redoc:   http://localhost:8000/redoc")
    logger.info("📄 openapi: http://localhost:8000/openapi.json")

    uvicorn.run(
        "api.main_api:app",   # 必须是模块路径字符串（启用 reload）
        host=host,
        port=port,
        reload=reload_flag,   # 开发 True；生产建议 False
        reload_dirs=abs_dirs,
        reload_includes=["**/*.py"],
        reload_delay=0.5,     # Windows/同步盘稍大一点更稳
    )
