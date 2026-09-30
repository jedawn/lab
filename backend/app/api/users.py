from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_admin
from app.core.response import ApiResponse, success
from app.models import User
from app.schemas import UserCreateRequest, UserUpdateRequest
from app.services import user_service

router = APIRouter(prefix="/api/users", tags=["用户管理"])


@router.get("", response_model=ApiResponse, summary="用户列表(分页+搜索)")
def list_users(
    keyword: str = Query("", description="搜索关键词(账号/昵称/邮箱/手机号)"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    data = user_service.list_users(db, keyword, page, page_size)
    return success(data=data)


@router.post("", response_model=ApiResponse, summary="新增用户")
def create_user(
    body: UserCreateRequest,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    data = user_service.create_user(db, body)
    return success(data=data, message="创建成功")


@router.put("/{user_id}", response_model=ApiResponse, summary="修改用户")
def update_user(
    user_id: int,
    body: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    data = user_service.update_user(db, current_user, user_id, body)
    return success(data=data, message="修改成功")


@router.delete("/{user_id}", response_model=ApiResponse, summary="删除用户")
def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user_service.delete_user(db, current_user, user_id)
    return success(message="删除成功")
