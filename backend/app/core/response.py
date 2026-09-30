from typing import Any, Optional

from pydantic import BaseModel


class ApiResponse(BaseModel):
    """统一响应结构:HTTP 状态码恒为 200,业务结果由 code 字段表达。"""

    code: int = 200
    message: str = "success"
    data: Optional[Any] = None


def success(data: Any = None, message: str = "success") -> ApiResponse:
    return ApiResponse(code=200, message=message, data=data)


def fail(code: int = 400, message: str = "请求失败") -> ApiResponse:
    return ApiResponse(code=code, message=message, data=None)


class BusinessError(Exception):
    """业务逻辑异常,由 service 层抛出,API 层捕获后转为统一响应"""

    def __init__(self, code: int = 400, message: str = "请求失败"):
        self.code = code
        self.message = message
        super().__init__(message)
