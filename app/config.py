"""
配置文件 - 宠忆星·云纪念馆
Configuration file for Pet Memory Star
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """应用配置类"""
    
    # 基础配置
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8000))
    
    # 数据库配置
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///pet_memorials.db')
    
    # 邮件配置
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.qq.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '1208155205@qq.com')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    
    # 文件存储路径
    STORAGE_PATH = os.getenv('STORAGE_PATH', 'storage')
    UPLOAD_MAX_SIZE = int(os.getenv('UPLOAD_MAX_SIZE', 10 * 1024 * 1024))  # 10MB
    
    # API配置
    API_V1_PREFIX = '/api'
    
    # 安全配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    
    @classmethod
    def get_database_url(cls):
        """获取数据库连接URL"""
        return cls.DATABASE_URL
    
    @classmethod
    def is_email_configured(cls):
        """检查邮件是否配置完整"""
        return bool(cls.SMTP_USERNAME and cls.SMTP_PASSWORD)

# 全局配置实例
config = Config()
