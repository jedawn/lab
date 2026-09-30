from contextlib import asynccontextmanager
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.auth import router as auth_router
from app.api.devices import router as devices_router
from app.api.labs import router as labs_router
from app.api.reservations import router as reservations_router
from app.api.test import router as test_router
from app.api.upload import router as upload_router
from app.api.users import router as users_router
from app.api.ai import router as ai_router
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.deps import AuthError
from app.core.response import ApiResponse, BusinessError
from app.core.security import hash_password
from app.models import Device, Lab, Reservation, User
from app.services.reservation_service import auto_cancel_expired


def _ensure_users_columns():
    """开发期轻量迁移:为已存在的 users 表补充新增列(create_all 不会改已存在的表)。"""
    from sqlalchemy import inspect, text

    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return
    existing = {c["name"] for c in inspector.get_columns("users")}
    needed = {"phone"}
    missing = needed - existing
    if not missing:
        return
    column_defs = {
        "phone": "VARCHAR(20) DEFAULT NULL COMMENT '手机号'",
    }
    with engine.begin() as conn:
        for col in missing:
            conn.execute(text(f"ALTER TABLE users ADD COLUMN {col} {column_defs[col]}"))


def init_db():
    """建表并初始化默认 admin 账号(账号 admin / 密码 123456)及示例实验室、设备数据。"""
    Base.metadata.create_all(bind=engine)
    _ensure_users_columns()
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == "admin").first():
            db.add(User(username="admin", password=hash_password("123456"), name="管理员"))
            db.commit()

        if not db.query(Lab).first():
            db.add_all([
                Lab(name="物理实验室", capacity=20, open_start="08:00", open_end="18:00", status=1),
                Lab(name="电子实验室", capacity=20, open_start="08:00", open_end="18:00", status=1),
                Lab(name="计算机实验室", capacity=20, status=1),
            ])
            db.commit()

        if not db.query(Device).first():
            labs = db.query(Lab).all()
            lab_map = {l.name: l.id for l in labs}
            db.add_all([
                Device(name="示波器", model_spec="DSO-X2024A", quantity=10, status=1, lab_id=lab_map.get("电子实验室", 1)),
                Device(name="万用表", model_spec="Fluke 87V", quantity=22, status=2, lab_id=lab_map.get("物理实验室", 1)),
            ])
            db.commit()
    finally:
        db.close()


def _auto_cancel_expired_job():
    """定时任务:扫描并自动取消过期未审核的预约。"""
    db = SessionLocal()
    try:
        auto_cancel_expired(db)
    except Exception as e:  # 定时任务内异常不能影响服务运行
        print(f"[auto_cancel_expired] 定时任务异常: {e}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # 后台定时调度:每 5 分钟自动取消过期未审核的预约,无需依赖请求触发
    scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
    scheduler.add_job(
        _auto_cancel_expired_job,
        "interval",
        minutes=5,
        id="auto-cancel-expired",
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()
    try:
        yield
    finally:
        scheduler.shutdown(wait=False)


app = FastAPI(title="LangGraph Project API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """参数校验失败时保持统一响应结构(HTTP 200 + 业务码 422)。"""
    errors = exc.errors()
    msg = errors[0].get("msg", "参数校验失败") if errors else "参数校验失败"
    msg = msg.removeprefix("Value error, ")  # 去掉 pydantic 对自定义校验器错误的英文前缀
    return JSONResponse(
        status_code=200,
        content=ApiResponse(code=422, message=msg).model_dump(),
    )


@app.exception_handler(AuthError)
async def auth_error_handler(request: Request, exc: AuthError):
    """鉴权/权限失败统一响应(HTTP 200 + 业务码 401/403)。"""
    return JSONResponse(
        status_code=200,
        content=ApiResponse(code=exc.code, message=exc.message).model_dump(),
    )


@app.exception_handler(BusinessError)
async def business_error_handler(request: Request, exc: BusinessError):
    """业务逻辑异常统一响应(HTTP 200 + 业务码)。"""
    return JSONResponse(
        status_code=200,
        content=ApiResponse(code=exc.code, message=exc.message).model_dump(),
    )


app.include_router(auth_router)
app.include_router(upload_router)
app.include_router(users_router)
app.include_router(labs_router)
app.include_router(devices_router)
app.include_router(reservations_router)
app.include_router(test_router)
app.include_router(ai_router)

# 挂载上传文件静态目录,前端可直接通过 /uploads/<文件名> 访问
upload_dir = Path(settings.UPLOAD_DIR)
upload_dir.mkdir(parents=True, exist_ok=True)
app.mount(f"/{settings.UPLOAD_DIR}", StaticFiles(directory=upload_dir), name="uploads")
