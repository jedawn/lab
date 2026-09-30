from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_admin
from app.core.response import ApiResponse, success
from app.models import User
from app.schemas import DeviceCreateRequest, DeviceUpdateRequest
from app.services import device_service

router = APIRouter(prefix="/api/devices", tags=["设备管理"])


@router.get("", response_model=ApiResponse, summary="设备列表(分页+搜索+实验室筛选)")
def list_devices(
    keyword: str = Query("", description="按设备名称搜索"),
    lab_id: int | None = Query(None, description="按实验室筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    db: Session = Depends(get_db),
):
    data = device_service.list_devices(db, keyword, lab_id, page, page_size)
    return success(data=data)


@router.post("", response_model=ApiResponse, summary="新增设备")
def create_device(
    body: DeviceCreateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    data = device_service.create_device(db, body)
    return success(data=data, message="创建成功")


@router.put("/{device_id}", response_model=ApiResponse, summary="修改设备")
def update_device(
    device_id: int,
    body: DeviceUpdateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    data = device_service.update_device(db, device_id, body)
    return success(data=data, message="修改成功")


@router.delete("/{device_id}", response_model=ApiResponse, summary="删除设备")
def delete_device(
    device_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    device_service.delete_device(db, device_id)
    return success(message="删除成功")
