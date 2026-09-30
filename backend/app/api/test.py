from fastapi import APIRouter

from app.core.response import ApiResponse, success

router = APIRouter(prefix="/api", tags=["测试"])


@router.get("/test", response_model=ApiResponse, summary="测试接口")
def test():
    """简单的测试接口,用于验证后端服务是否正常运行。"""
    return success(message="Hello from backend")
