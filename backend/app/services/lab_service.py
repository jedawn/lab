from sqlalchemy import Select
from sqlalchemy.orm import Session

from app.core.response import BusinessError
from app.models import Device, Lab
from app.schemas import LabCreateRequest, LabListItem, LabUpdateRequest


def list_labs(db: Session, keyword: str, page: int, page_size: int, status: int | None = None) -> dict:
    """实验室列表(分页+按名称搜索+状态筛选)。"""
    query = db.query(Lab)
    if keyword.strip():
        query = query.filter(Lab.name.like(f"%{keyword.strip()}%"))
    if status is not None:
        query = query.filter(Lab.status == status)
    total = query.count()
    rows = (
        query.order_by(Lab.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "total": total,
        "list": [LabListItem.model_validate(r).model_dump() for r in rows],
    }


def get_lab(db: Session, lab_id: int) -> dict:
    """实验室详情。"""
    lab = db.get(Lab, lab_id)
    if not lab:
        raise BusinessError(code=404, message="实验室不存在")
    return LabListItem.model_validate(lab).model_dump()


def create_lab(db: Session, body: LabCreateRequest) -> dict:
    """新增实验室:名称唯一校验。"""
    stmt = Select(Lab).where(Lab.name == body.name)
    exist_lab = db.scalar(stmt)
    if exist_lab:
        raise BusinessError(code=400, message="实验室已存在,请重新命名")
    lab = Lab(
        name=body.name,
        intro=body.intro,
        cover=body.cover,
        location=body.location,
        capacity=body.capacity,
        open_start=body.open_start,
        open_end=body.open_end,
        status=body.status,
    )
    db.add(lab)
    db.commit()
    db.refresh(lab)
    return LabListItem.model_validate(lab).model_dump()


def update_lab(db: Session, lab_id: int, body: LabUpdateRequest) -> dict:
    """修改实验室:按字段可选更新。"""
    lab = db.get(Lab, lab_id)
    if not lab:
        raise BusinessError(code=404, message="实验室不存在")

    if body.name is not None:
        lab.name = body.name
    if body.intro is not None:
        lab.intro = body.intro or None
    if body.cover is not None:
        lab.cover = body.cover or None
    if body.location is not None:
        lab.location = body.location or None
    if body.capacity is not None:
        lab.capacity = body.capacity
    if body.open_start is not None:
        lab.open_start = body.open_start or None
    if body.open_end is not None:
        lab.open_end = body.open_end or None
    if body.status is not None:
        lab.status = body.status

    db.commit()
    db.refresh(lab)
    return LabListItem.model_validate(lab).model_dump()


def delete_lab(db: Session, lab_id: int) -> None:
    """删除实验室:有关联设备时拒绝,避免外键约束报错。"""
    lab = db.get(Lab, lab_id)
    if not lab:
        raise BusinessError(code=404, message="实验室不存在")
    # 检查是否有关联设备,避免外键约束报错
    device_count = db.query(Device).filter(Device.lab_id == lab_id).count()
    if device_count > 0:
        raise BusinessError(code=400, message=f"该实验室下有 {device_count} 个设备,请先移除或转移设备后再删除")
    db.delete(lab)
    db.commit()
