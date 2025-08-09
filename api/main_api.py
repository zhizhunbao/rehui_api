# main_api.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from controller.car_controller import router as car_router
from utils.logger import Logger


# ======== 参数变量 ========
app_title     = "Rehui API"
app_version   = "v1"
host          = "0.0.0.0"
port          = 8000
reload_flag   = True

# 只监听这些目录（加快热加载）
reload_dirs   = ["api", "controller", "services", "core"]


# ======== 工具对象 ========
logger = Logger.get_global_logger()
app    = FastAPI(title=app_title, version=app_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发全开，生产可限制域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(car_router)


# ======== 健康检查 ========
@app.get("/healthz")
def healthz():
    return {"status": "ok"}


# ======== 启动事件 ========
@app.on_event("startup")
async def _on_startup():
    logger.info("🚀 服务启动成功！")
    logger.info("📎 Swagger 文档：http://localhost:8000/docs")
    logger.info("📎 Redoc 文档：http://localhost:8000/redoc")


# ======== 开发模式启动 ========
if __name__ == "__main__":
    import uvicorn
    logger.info("🔧 使用精简热加载（只监听核心目录） ...")
    uvicorn.run(
        "main_api:app",
        host=host,
        port=port,
        reload=reload_flag,
        reload_dirs=reload_dirs
    )
