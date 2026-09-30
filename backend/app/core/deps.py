from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models import User


class AuthError(Exception):
    """鉴权/权限失败。code=401 表示未登录/token 失效;code=403 表示无权限。"""

    def __init__(self, message: str = "登录状态已失效,请重新登录", code: int = 401):
        self.message = message
        self.code = code
        super().__init__(message)


# auto_error=False:不直接返回 401,改为抛出自定义 AuthError,走统一响应结构
_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """鉴权依赖:从 Authorization: Bearer <token> 解析当前登录用户。"""
    if credentials is None:
        raise AuthError("未登录或登录已失效")
    try:
        user_id = decode_access_token(credentials.credentials)
    except JWTError:
        raise AuthError("登录已过期,请重新登录")
    user = db.get(User, int(user_id))
    if user is None:
        raise AuthError("用户不存在或已失效")
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """管理员鉴权:仅 role=admin 可访问,否则返回业务码 403。"""
    if current_user.role != "admin":
        raise AuthError("无权限执行此操作", code=403)
    return current_user
