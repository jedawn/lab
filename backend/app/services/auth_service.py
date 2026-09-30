from sqlalchemy.orm import Session

from app.core.response import BusinessError
from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.schemas import (
    LoginRequest,
    PasswordChangeRequest,
    ProfileUpdateRequest,
    RegisterRequest,
    UserInfo,
)


def login(db: Session, body: LoginRequest) -> dict:
    """用户登录:校验账号密码,签发 token。"""
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not verify_password(body.password, user.password):
        raise BusinessError(code=401, message="账号或密码错误")
    token = create_access_token(subject=str(user.id))
    return {
        "token": token,
        "user": UserInfo.model_validate(user).model_dump(),
    }


def register(db: Session, body: RegisterRequest) -> None:
    """用户注册:用户名唯一校验 + 写入默认 role=user 的用户。"""
    if db.query(User).filter(User.username == body.username).first():
        raise BusinessError(code=400, message="用户名已存在")
    db.add(
        User(
            username=body.username,
            password=hash_password(body.password),
            name=body.username,
            role="user",
        )
    )
    db.commit()


def get_current_user_info(current_user: User) -> dict:
    """返回当前登录用户信息。"""
    return UserInfo.model_validate(current_user).model_dump()


def update_profile(db: Session, current_user: User, body: ProfileUpdateRequest) -> dict:
    """修改昵称、邮箱、头像、手机号;账号和角色不可改。"""
    # 邮箱唯一性校验(排除自己)
    if body.email:
        exists = (
            db.query(User)
            .filter(User.email == body.email, User.id != current_user.id)
            .first()
        )
        if exists:
            raise BusinessError(code=400, message="该邮箱已被其他用户使用")

    current_user.name = body.name
    current_user.email = body.email
    current_user.avatar = body.avatar
    current_user.phone = body.phone
    db.commit()
    return UserInfo.model_validate(current_user).model_dump()


def change_password(db: Session, current_user: User, body: PasswordChangeRequest) -> None:
    """当前用户修改自己的密码:需验证原密码,新密码 bcrypt 加密后存储。"""
    if not verify_password(body.old_password, current_user.password):
        raise BusinessError(code=400, message="原密码错误")
    current_user.password = hash_password(body.new_password)
    db.commit()
