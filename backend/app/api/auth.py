from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.response import ApiResponse, success
from app.models import User
from app.schemas import (
    LoginRequest,
    PasswordChangeRequest,
    ProfileUpdateRequest,
    RegisterRequest,
)
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/login", response_model=ApiResponse, summary="用户登录")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    data = auth_service.login(db, body)
    return success(data=data, message="登录成功")


@router.post("/register", response_model=ApiResponse, summary="用户注册")
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    auth_service.register(db, body)
    return success(message="注册成功,请登录")


@router.get("/me", response_model=ApiResponse, summary="获取当前登录用户信息")
def me(current_user: User = Depends(get_current_user)):
    """供前端刷新页面后校验 token 是否有效,并恢复当前用户信息。"""
    return success(data=auth_service.get_current_user_info(current_user))


@router.put("/profile", response_model=ApiResponse, summary="修改当前用户个人信息")
def update_profile(
    body: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """修改昵称、邮箱、头像、手机号;账号和角色不可改。"""
    data = auth_service.update_profile(db, current_user, body)
    return success(data=data, message="修改成功")


@router.put("/password", response_model=ApiResponse, summary="修改当前用户密码")
def change_password(
    body: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """当前用户修改自己的密码:需验证原密码,新密码 bcrypt 加密后存储。"""
    auth_service.change_password(db, current_user, body)
    return success(message="密码修改成功,请重新登录")
