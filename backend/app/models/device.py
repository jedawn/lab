from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Device(Base):
    __tablename__ = "devices"
    __table_args__ = {"comment": "实验室设备表"}

    name: Mapped[str] = mapped_column(String(128), comment="设备名称")
    image: Mapped[str | None] = mapped_column(String(255), default=None, comment="设备图片URL")
    model_spec: Mapped[str | None] = mapped_column(String(255), default=None, comment="型号规格")
    quantity: Mapped[int] = mapped_column(Integer, default=1, comment="数量")
    status: Mapped[int] = mapped_column(Integer, default=1, comment="状态(1正常/2维修)")
    lab_id: Mapped[int] = mapped_column(Integer, ForeignKey("labs.id"), comment="所属实验室ID")
