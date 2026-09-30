from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin
from app.core.response import ApiResponse, success
from app.models import User
from app.schemas import (
    ReservationAuditRequest,
    ReservationCreateRequest,
)
from app.services import reservation_service

router = APIRouter(prefix="/api/reservations", tags=["实验室预约"])


@router.get("", response_model=ApiResponse, summary="我的预约列表(分页+状态筛选)")
def list_my_reservations(
    status: int | None = Query(None, description="按状态筛选(1待审核/2已通过/3已拒绝/4已取消/5已过期)"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = reservation_service.list_my_reservations(db, current_user, status, page, page_size)
    return success(data=data)


@router.get("/all", response_model=ApiResponse, summary="管理员-全部预约列表(分页+筛选)")
def list_all_reservations(
    status: int | None = Query(None, description="按状态筛选"),
    keyword: str = Query("", description="按实验室名/用户名/账号搜索"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    data = reservation_service.list_all_reservations(db, status, keyword, page, page_size)
    return success(data=data)


@router.post("", response_model=ApiResponse, summary="创建预约")
def create_reservation(
    body: ReservationCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = reservation_service.create_reservation(db, current_user, body)
    return success(data=data, message="预约成功,请等待管理员审核")


@router.put("/{reservation_id}/cancel", response_model=ApiResponse, summary="取消我的预约")
def cancel_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reservation_service.cancel_reservation(db, current_user, reservation_id)
    return success(message="已取消")


@router.put("/{reservation_id}/audit", response_model=ApiResponse, summary="管理员审核预约")
def audit_reservation(
    reservation_id: int,
    body: ReservationAuditRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    message = reservation_service.audit_reservation(db, reservation_id, body)
    return success(message=message)
