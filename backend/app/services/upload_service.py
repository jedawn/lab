import os
import secrets
import shutil
import time
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings
from app.core.response import BusinessError
from app.schemas import UploadResult


class _CountingWriter:
    """包装文件对象,统计写入字节数,供 shutil.copyfileobj 边写边计数。"""

    def __init__(self, fp):
        self.fp = fp
        self.count = 0

    def write(self, b):
        n = self.fp.write(b)
        self.count += n
        if self.count > settings.MAX_FILE_SIZE:
            raise OverflowError("file too large")
        return n

    def flush(self):
        self.fp.flush()


def _safe_ext(filename: str) -> str:
    """提取并规范化扩展名(小写,含点)。"""
    return os.path.splitext(filename or "")[1].lower()


def upload_file(file: UploadFile) -> dict:
    """流式上传文件,避免大文件占用过多内存。

    - 校验扩展名与大小(边写边计,超限立即停止并清理)
    - 使用 shutil.copyfileobj 分块写入磁盘
    - 磁盘文件名:毫秒时间戳_8位随机hex.扩展名
    """
    ext = _safe_ext(file.filename)
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise BusinessError(code=400, message=f"不支持的文件类型:{ext or '无扩展名'}")

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    disk_name = f"{int(time.time() * 1000)}_{secrets.token_hex(4)}{ext}"
    dest = upload_dir / disk_name

    written = 0
    try:
        with dest.open("wb") as out:
            counter = _CountingWriter(out)
            # copyfileobj 内部以 64KB 为单位循环读取上传流并写入,避免一次性读入内存
            shutil.copyfileobj(file.file, counter, length=64 * 1024)
            written = counter.count
    except OverflowError:
        dest.unlink(missing_ok=True)
        raise BusinessError(
            code=413,
            message=f"文件过大,最大允许 {settings.MAX_FILE_SIZE // (1024 * 1024)}MB",
        )
    except Exception:
        dest.unlink(missing_ok=True)
        raise
    finally:
        file.file.close()

    return UploadResult(
        original_name=file.filename or "",
        disk_name=disk_name,
        size=written,
        url=f"/{settings.UPLOAD_DIR}/{disk_name}",
    ).model_dump()
