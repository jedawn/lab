from pydantic import BaseModel


class UploadResult(BaseModel):
    """文件上传成功后的返回信息。"""

    original_name: str  # 原始文件名
    disk_name: str      # 磁盘存储文件名
    size: int           # 文件大小(字节)
    url: str            # 静态访问路径
