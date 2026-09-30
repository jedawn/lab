from datetime import datetime

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"comment": "用户表"}

    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, comment="登录账号")
    password: Mapped[str] = mapped_column(String(255), comment="加密后的密码")
    role: Mapped[str] = mapped_column(String(64), default="user", comment="用户角色", nullable=False)
    email: Mapped[str | None] = mapped_column(String(64), unique=True, index=True, comment="邮箱")
    name: Mapped[str] = mapped_column(String(64), default="", comment="用户昵称")
    avatar: Mapped[str | None] = mapped_column(String(255), default=None, comment="用户头像")
    phone: Mapped[str | None] = mapped_column(String(20), default=None, comment="手机号")
    status: Mapped[int] = mapped_column(default=1, comment="用户状态")
