from fastapi import APIRouter, UploadFile, File

from app.core.response import ApiResponse, BusinessError, fail, success
from app.services.upload_service import upload_file

router = APIRouter(prefix="/api", tags=["文件上传"])


@router.post("/upload", response_model=ApiResponse, summary="文件上传")
def upload(file: UploadFile = File(...)):
    """流式上传文件,避免大文件占用过多内存。

    - 校验扩展名与大小(边写边计,超限立即停止并清理)
    - 使用 shutil.copyfileobj 分块写入磁盘
    - 磁盘文件名:毫秒时间戳_8位随机hex.扩展名
    """
    try:
        data = upload_file(file)
    except BusinessError:
        raise
    except Exception as e:
        return fail(code=500, message=f"文件保存失败:{e}")
    return success(data=data, message="请求成功")
