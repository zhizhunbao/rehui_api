# controller/car_controller.py
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from services.car_value_analysis_service import evaluate_from_url
from utils.logger import Logger


# ======== 参数变量 ========
api_prefix        = "/api"            # 路由前缀
route_path        = "/evaluate"       # 评估路由
success_code      = 0                 # 业务成功码
bad_request_code  = 40001             # 参数/数据问题
server_error_code = 50001             # 未知异常

# ======== 工具对象 ========
router = APIRouter(prefix=api_prefix, tags=["Evaluate"])
logger = Logger.get_global_logger()

class EvaluateRequest(BaseModel):
    url: str


# ======== 路由：这车值不值 ========
@router.post(route_path)
def evaluate_car_value(req: EvaluateRequest):
    logger.info(f"🔍 接收到评估请求: {req.url}")

    try:
        data = evaluate_from_url(req.url)
        return JSONResponse(
            status_code=200,
            content={"code": success_code, "message": "success", "data": data},
        )
    except ValueError as e:
        logger.warning(f"⚠️ 业务校验失败: {e}")
        return JSONResponse(
            status_code=400,
            content={"code": bad_request_code, "message": str(e), "data": None},
        )
    except Exception as e:
        logger.exception(f"💥 服务异常: {e}")
        return JSONResponse(
            status_code=500,
            content={"code": server_error_code, "message": "Internal Server Error", "data": None},
        )