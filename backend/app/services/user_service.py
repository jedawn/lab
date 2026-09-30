from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.response import BusinessError
from app.core.security import hash_password
from app.models import User
from app.schemas import UserCreateRequest, UserListItem, UserUpdateRequest


def list_users(db: Session, keyword: str, page: int, page_size: int) -> dict:
    """用户列表(分页+按账号/昵称/邮箱/手机号搜索)。"""
    query = db.query(User)
    if keyword.strip():
        kw = f"%{keyword.strip()}%"
        query = query.filter(
            or_(
                User.username.like(kw),
                User.name.like(kw),
                User.email.like(kw),
                User.phone.like(kw),
            )
        )
    total = query.count()
    rows = (
        query.order_by(User.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "total": total,
        "list": [UserListItem.model_validate(r).model_dump() for r in rows],
    }


def create_user(db: Session, body: UserCreateRequest) -> dict:
    """新增用户:账号/邮箱唯一性校验后写入。"""
    if db.query(User).filter(User.username == body.username).first():
        raise BusinessError(code=400, message="账号已存在")
    if body.email:
        exists = db.query(User).filter(User.email == body.email).first()
        if exists:
            raise BusinessError(code=400, message="该邮箱已被使用")
    user = User(
        username=body.username,
        password=hash_password(body.password),
        name=body.name or body.username,
        role=body.role,
        email=body.email,
        phone=body.phone,
        status=body.status,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserListItem.model_validate(user).model_dump()


def update_user(db: Session, current_user: User, user_id: int, body: UserUpdateRequest) -> dict:
    """修改用户:禁止管理员修改自己的角色,邮箱唯一性校验(排除自己)。"""
    user = db.get(User, user_id)
    if not user:
        raise BusinessError(code=404, message="用户不存在")

    # 禁止管理员修改自己的角色
    if (
        user_id == current_user.id
        and body.role is not None
        and body.role != current_user.role
    ):
        raise BusinessError(code=400, message="不能修改自己的角色")

    if body.email is not None:
        exists = (
            db.query(User)
            .filter(User.email == body.email, User.id != user_id)
            .first()
        )
        if exists:
            raise BusinessError(code=400, message="该邮箱已被其他用户使用")

    if body.name is not None:
        user.name = body.name
    if body.role is not None:
        user.role = body.role
    if body.email is not None:
        user.email = body.email or None
    if body.phone is not None:
        user.phone = body.phone or None
    if body.status is not None:
        user.status = body.status
    if body.password:
        user.password = hash_password(body.password)

    db.commit()
    db.refresh(user)
    return UserListItem.model_validate(user).model_dump()


def delete_user(db: Session, current_user: User, user_id: int) -> None:
    """删除用户:禁止删除当前登录的管理员账号。"""
    if user_id == current_user.id:
        raise BusinessError(code=400, message="不能删除当前登录的管理员账号")
    user = db.get(User, user_id)
    if not user:
        raise BusinessError(code=404, message="用户不存在")
    db.delete(user)
    db.commit()
