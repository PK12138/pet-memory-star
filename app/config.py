import os

class Config:
    # 邮件服务配置
    SMTP_SERVER = "smtp.qq.com"
    SMTP_PORT = 587
    SENDER_EMAIL = "1208155205@qq.com"
    SENDER_PASSWORD = "tscvmzpbazgbbaeh"

    # 服务器配置
    SERVER_BASE_URL = "http://42.193.230.145"  # 生产环境服务器地址
    LOCAL_BASE_URL = "http://localhost:8000"    # 本地开发地址

    # 根据环境变量选择服务器地址
    if os.getenv('ENVIRONMENT') == 'production':
        BASE_URL = SERVER_BASE_URL
    else:
        BASE_URL = LOCAL_BASE_URL

    # DeepSeek API配置
    DEEPSEEK_API_KEY = "sk-f791e06a786145aaa715342d97df3591"
    DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

    # 安全配置
    SECRET_KEY = "pet-memory-star-2024-secure-key-pk12138-production"

    # 数据库配置
    DATABASE_URL = "sqlite:///pet_memorials.db"

    # 文件存储路径
    STORAGE_PATH = "storage"
    MEMORIALS_PATH = "storage/memorials"
    PHOTOS_PATH = "storage/photos"

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
