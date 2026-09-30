from sqlalchemy.orm import Session

from app.core.response import BusinessError
from app.models import Device, Lab
from app.schemas import DeviceCreateRequest, DeviceListItem, DeviceUpdateRequest


def _to_list_item(device: Device, lab_name: str = "") -> dict:
    item = DeviceListItem.model_validate(device)
    item.lab_name = lab_name
    return item.model_dump()


def list_devices(
    db: Session, keyword: str, lab_id: int | None, page: int, page_size: int
) -> dict:
    """设备列表(分页+按名称搜索+按实验室筛选),关联实验室名称。"""
    query = db.query(Device, Lab.name).outerjoin(Lab, Device.lab_id == Lab.id)
    if keyword.strip():
        query = query.filter(Device.name.like(f"%{keyword.strip()}%"))
    if lab_id is not None:
        query = query.filter(Device.lab_id == lab_id)

    total = query.count()
    rows = (
        query.order_by(Device.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "total": total,
        "list": [_to_list_item(d, lab_name) for d, lab_name in rows],
    }


def create_device(db: Session, body: DeviceCreateRequest) -> dict:
    """新增设备:校验所属实验室存在。"""
    if not db.get(Lab, body.lab_id):
        raise BusinessError(code=400, message="所属实验室不存在")
    device = Device(
        name=body.name,
        image=body.image,
        model_spec=body.model_spec,
        quantity=body.quantity,
        status=body.status,
        lab_id=body.lab_id,
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    lab = db.get(Lab, device.lab_id)
    return _to_list_item(device, lab.name if lab else "")


def update_device(db: Session, device_id: int, body: DeviceUpdateRequest) -> dict:
    """修改设备:按字段可选更新,切换实验室时校验存在性。"""
    device = db.get(Device, device_id)
    if not device:
        raise BusinessError(code=404, message="设备不存在")

    if body.lab_id is not None and not db.get(Lab, body.lab_id):
        raise BusinessError(code=400, message="所属实验室不存在")

    if body.name is not None:
        device.name = body.name
    if body.image is not None:
        device.image = body.image or None
    if body.model_spec is not None:
        device.model_spec = body.model_spec or None
    if body.quantity is not None:
        device.quantity = body.quantity
    if body.status is not None:
        device.status = body.status
    if body.lab_id is not None:
        device.lab_id = body.lab_id

    db.commit()
    db.refresh(device)
    lab = db.get(Lab, device.lab_id)
    return _to_list_item(device, lab.name if lab else "")


def delete_device(db: Session, device_id: int) -> None:
    """删除设备。"""
    device = db.get(Device, device_id)
    if not device:
        raise BusinessError(code=404, message="设备不存在")
    db.delete(device)
    db.commit()
