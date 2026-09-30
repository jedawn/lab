from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # MySQL 数据库配置
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "123456"
    DB_NAME: str = "lab_system"

    # JWT 配置
    JWT_SECRET_KEY: str = "change-this-to-a-random-secret-key-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    # 文件上传配置
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {
        # 图片
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg",
        # 文档
        ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
        # 文本
        ".txt", ".csv", ".md", ".json",
        # 压缩
        ".zip", ".rar", ".7z",
    }
    # 大模型相关的配置
    DASHSCOPE_API_KEY: str = ""
    BASE_URL: str = "https://ws-89tbx7taehfjlkhj.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"
    LLM_MODEL: str = "qwen3.7-flash"
    EMBED_MODEL: str = "text-embedding-v4"

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
