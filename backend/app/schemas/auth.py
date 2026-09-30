from pydantic import BaseModel, Field, ConfigDict, model_validator


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, description="登录账号")
    password: str = Field(..., min_length=1, description="密码")


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=32, description="用户名")
    password: str = Field(..., min_length=6, max_length=64, description="密码")
    confirm_password: str = Field(..., min_length=6, max_length=64, description="确认密码")

    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("两次输入的密码不一致")
        return self


class UserInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # 允许从 ORM 对象按属性映射
    id: int
    username: str
    name: str
    role: str
    email: str | None = None
    avatar: str | None = None
    phone: str | None = None


class ProfileUpdateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=64, description="昵称")
    email: str | None = Field(None, max_length=64, description="邮箱")
    avatar: str | None = Field(None, max_length=255, description="头像URL")
    phone: str | None = Field(None, max_length=20, description="手机号")


class PasswordChangeRequest(BaseModel):
    old_password: str = Field(..., min_length=1, description="原密码")
    new_password: str = Field(..., min_length=6, max_length=64, description="新密码")
    confirm_password: str = Field(..., min_length=6, max_length=64, description="确认新密码")

    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.new_password != self.confirm_password:
            raise ValueError("两次输入的密码不一致")
        return self
