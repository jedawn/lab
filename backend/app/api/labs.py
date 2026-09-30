from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_admin
from app.core.response import ApiResponse, success
from app.models import User
from app.schemas import LabCreateRequest, LabUpdateRequest
from app.services import lab_service

router = APIRouter(prefix="/api/labs", tags=["实验室管理"])


@router.get("", response_model=ApiResponse, summary="实验室列表(分页+搜索)")
def list_labs(
    keyword: str = Query("", description="按名称搜索"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    db: Session = Depends(get_db),
):
    data = lab_service.list_labs(db, keyword, page, page_size)
    return success(data=data)


@router.get("/{lab_id}", response_model=ApiResponse, summary="实验室详情")
def get_lab(lab_id: int, db: Session = Depends(get_db)):
    data = lab_service.get_lab(db, lab_id)
    return success(data=data)


@router.post("", response_model=ApiResponse, summary="新增实验室")
def create_lab(
    body: LabCreateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    data = lab_service.create_lab(db, body)
    return success(data=data, message="创建成功")


@router.put("/{lab_id}", response_model=ApiResponse, summary="修改实验室")
def update_lab(
    lab_id: int,
    body: LabUpdateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    data = lab_service.update_lab(db, lab_id, body)
    return success(data=data, message="修改成功")


@router.delete("/{lab_id}", response_model=ApiResponse, summary="删除实验室")
def delete_lab(
    lab_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    lab_service.delete_lab(db, lab_id)
    return success(message="删除成功")
