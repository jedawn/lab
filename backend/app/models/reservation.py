from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Reservation(Base):
    __tablename__ = "reservations"
    __table_args__ = {"comment": "实验室预约表"}

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), comment="预约用户ID")
    lab_id: Mapped[int] = mapped_column(Integer, ForeignKey("labs.id"), comment="实验室ID")
    device_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("devices.id"), default=None, comment="设备ID(为空表示预约整个实验室)"
    )
    date: Mapped[str] = mapped_column(String(10), comment="预约日期(YYYY-MM-DD)")
    start_time: Mapped[str | None] = mapped_column(String(5), default=None, comment="开始时间(HH:MM)")
    end_time: Mapped[str | None] = mapped_column(String(5), default=None, comment="结束时间(HH:MM)")
    remark: Mapped[str | None] = mapped_column(String(500), default=None, comment="备注")
    status: Mapped[int] = mapped_column(Integer, default=1, comment="状态(1待审核/2已通过/3已拒绝/4已取消)")
