from datetime import date as date_cls, datetime, time as time_cls

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.response import BusinessError
from app.models import Device, Lab, Reservation, User
from app.schemas import (
    ReservationAuditRequest,
    ReservationCreateRequest,
    ReservationListItem,
)


def _is_expired(reservation: Reservation) -> bool:
    """预约时间是否已过(用于自动取消未审核预约)。

    规则:预约日期早于今天 → 过期;
    预约日期为今天且有具体时段 → 当前时间晚于结束时间(无结束时间则看开始时间)即过期;
    预约日期为今天且无具体时段 → 不立即取消,留到次日。
    """
    try:
        d = date_cls.fromisoformat(reservation.date)
    except (ValueError, TypeError):
        return False
    today = date_cls.today()
    if d < today:
        return True
    if d > today:
        return False
    # 同一天:看具体时段
    t_str = reservation.end_time or reservation.start_time
    if not t_str:
        return False
    try:
        t = time_cls.fromisoformat(t_str)
    except ValueError:
        return False
    return datetime.now().time() > t


def auto_cancel_expired(db: Session) -> None:
    """将过期且仍待审核的预约自动标记为已过期(status=5)。

    供后台定时任务与列表查询接口复用,保证过期预约即使无人查询也会被处理。
    """
    pending = db.query(Reservation).filter(Reservation.status == 1).all()
    changed = False
    for r in pending:
        if _is_expired(r):
            r.status = 5
            changed = True
    if changed:
        db.commit()


def _to_list_item(
    reservation: Reservation,
    lab_name: str = "",
    device_name: str = "",
    user_name: str = "",
) -> dict:
    item = ReservationListItem.model_validate(reservation)
    item.lab_name = lab_name
    item.device_name = device_name
    item.user_name = user_name
    return item.model_dump()


def list_my_reservations(
    db: Session, current_user: User, status: int | None, page: int, page_size: int
) -> dict:
    """我的预约列表(分页+状态筛选),先触发一次过期自动取消。"""
    auto_cancel_expired(db)
    query = (
        db.query(Reservation, Lab.name, Device.name, User.name, User.username)
        .outerjoin(Lab, Reservation.lab_id == Lab.id)
        .outerjoin(Device, Reservation.device_id == Device.id)
        .outerjoin(User, Reservation.user_id == User.id)
        .filter(Reservation.user_id == current_user.id)
    )
    if status is not None:
        query = query.filter(Reservation.status == status)

    total = query.count()
    rows = (
        query.order_by(Reservation.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "total": total,
        "list": [
            _to_list_item(r, lab_name, device_name or "", nickname or username or "")
            for r, lab_name, device_name, nickname, username in rows
        ],
    }


def list_all_reservations(
    db: Session, status: int | None, keyword: str, page: int, page_size: int
) -> dict:
    """管理员-全部预约列表(分页+状态/关键词筛选),先触发一次过期自动取消。"""
    auto_cancel_expired(db)
    query = (
        db.query(Reservation, Lab.name, Device.name, User.name, User.username)
        .outerjoin(Lab, Reservation.lab_id == Lab.id)
        .outerjoin(Device, Reservation.device_id == Device.id)
        .outerjoin(User, Reservation.user_id == User.id)
    )
    if status is not None:
        query = query.filter(Reservation.status == status)
    kw = keyword.strip()
    if kw:
        like = f"%{kw}%"
        query = query.filter(
            or_(Lab.name.like(like), User.name.like(like), User.username.like(like))
        )

    total = query.count()
    rows = (
        query.order_by(Reservation.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "total": total,
        "list": [
            _to_list_item(r, lab_name, device_name or "", nickname or username or "")
            for r, lab_name, device_name, nickname, username in rows
        ],
    }


def create_reservation(
    db: Session, current_user: User, body: ReservationCreateRequest
) -> dict:
    """创建预约:校验实验室可用性、设备归属、时间区间后写入待审核记录。"""
    lab = db.get(Lab, body.lab_id)
    if not lab:
        raise BusinessError(code=400, message="实验室不存在")
    if lab.status != 1:
        raise BusinessError(code=400, message="该实验室已禁用,暂不可预约")

    device_name = ""
    if body.device_id is not None:
        device = db.get(Device, body.device_id)
        if not device:
            raise BusinessError(code=400, message="设备不存在")
        if device.lab_id != body.lab_id:
            raise BusinessError(code=400, message="设备与实验室不匹配")
        device_name = device.name

    # 时间区间校验:两者都填了时,结束时间必须晚于开始时间
    if body.start_time and body.end_time and body.end_time <= body.start_time:
        raise BusinessError(code=400, message="结束时间必须晚于开始时间")

    reservation = Reservation(
        user_id=current_user.id,
        lab_id=body.lab_id,
        device_id=body.device_id,
        date=body.date,
        start_time=body.start_time,
        end_time=body.end_time,
        remark=body.remark,
        status=1,
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return _to_list_item(
        reservation, lab.name, device_name, current_user.name or current_user.username
    )


def cancel_reservation(
    db: Session, current_user: User, reservation_id: int
) -> None:
    """取消自己的预约:仅本人且状态为待审核时可取消。"""
    reservation = db.get(Reservation, reservation_id)
    if not reservation:
        raise BusinessError(code=404, message="预约记录不存在")
    if reservation.user_id != current_user.id:
        raise BusinessError(code=403, message="只能取消自己的预约")
    if reservation.status != 1:
        raise BusinessError(code=400, message="仅待审核的预约可以取消")

    reservation.status = 4
    db.commit()


def audit_reservation(
    db: Session, reservation_id: int, body: ReservationAuditRequest
) -> str:
    """管理员审核预约:仅待审核记录可审核,返回审核结果文案。"""
    if body.status not in (2, 3):
        raise BusinessError(code=400, message="审核结果非法")
    reservation = db.get(Reservation, reservation_id)
    if not reservation:
        raise BusinessError(code=404, message="预约记录不存在")
    if reservation.status != 1:
        raise BusinessError(code=400, message="该预约已处理,不能重复审核")

    reservation.status = body.status
    db.commit()
    return "已通过" if body.status == 2 else "已拒绝"
