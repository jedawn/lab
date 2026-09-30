from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserCreateRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=32, description="登录账号")
    password: str = Field(..., min_length=6, max_length=64, description="密码")
    name: str | None = Field(None, max_length=64, description="昵称")
    role: str = Field("user", description="角色(admin/user)")
    email: str | None = Field(None, max_length=64, description="邮箱")
    phone: str | None = Field(None, max_length=20, description="手机号")
    status: int = Field(1, description="状态(1启用/0禁用)")


class UserUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=64, description="昵称")
    role: str | None = Field(None, description="角色(admin/user)")
    email: str | None = Field(None, max_length=64, description="邮箱")
    phone: str | None = Field(None, max_length=20, description="手机号")
    status: int | None = Field(None, description="状态(1启用/0禁用)")
    password: str | None = Field(None, min_length=6, max_length=64, description="重置密码(留空不修改)")


class UserListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    name: str
    role: str
    email: str | None = None
    avatar: str | None = None
    phone: str | None = None
    status: int
    create_time: datetime
