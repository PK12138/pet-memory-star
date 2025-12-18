import os


class Config:
    """
    配置统一从环境变量读取，避免将敏感信息写入代码仓库。
    本地开发可使用 `.env` 或在启动命令中导出环境变量。
    """

    # 邮件服务配置
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.qq.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")

    # 服务器配置
    SERVER_BASE_URL = os.getenv("SERVER_BASE_URL", "https://www.pettrailstar.cn")
    LOCAL_BASE_URL = os.getenv("LOCAL_BASE_URL", "http://localhost:8000")

    # 根据环境变量选择服务器地址
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    BASE_URL = SERVER_BASE_URL if ENVIRONMENT == "production" else LOCAL_BASE_URL

    # DeepSeek API配置
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")

    # 安全配置（生产环境必须设置）
    SECRET_KEY = os.getenv("SECRET_KEY", "pet-memory-star-dev-secret")

    # 数据库配置
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///pet_memorials.db")

    # 文件存储路径
    STORAGE_PATH = os.getenv("STORAGE_PATH", "storage")
    MEMORIALS_PATH = os.getenv("MEMORIALS_PATH", "storage/memorials")
    PHOTOS_PATH = os.getenv("PHOTOS_PATH", "storage/photos")

    @classmethod
    def get_database_url(cls):
        return cls.DATABASE_URL

    @classmethod
    def get_storage_path(cls):
        return cls.STORAGE_PATH

    @classmethod
    def get_memorials_path(cls):
        return cls.MEMORIALS_PATH

    @classmethod
    def get_photos_path(cls):
        return cls.PHOTOS_PATH

# 创建全局配置实例
config = Config()
