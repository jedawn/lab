from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Lab(Base):
    __tablename__ = "labs"
    __table_args__ = {"comment": "实验室表"}

    name: Mapped[str] = mapped_column(String(128), comment="实验室名称")
    intro: Mapped[str | None] = mapped_column(String(500), default=None, comment="简介")
    cover: Mapped[str | None] = mapped_column(String(255), default=None, comment="封面图URL")
    location: Mapped[str | None] = mapped_column(String(255), default=None, comment="位置")
    capacity: Mapped[int] = mapped_column(Integer, default=1, comment="容纳人数")
    open_start: Mapped[str | None] = mapped_column(String(5), default=None, comment="开放开始时间(HH:MM)")
    open_end: Mapped[str | None] = mapped_column(String(5), default=None, comment="开放结束时间(HH:MM)")
    status: Mapped[int] = mapped_column(Integer, default=1, comment="状态(1正常/0禁用)")
