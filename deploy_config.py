#!/usr/bin/env python3
"""
部署配置脚本 - 设置服务器地址和环境变量
"""

import os
import sys

def set_environment_variables():
    """设置环境变量"""
    print("=== 设置环境变量 ===")
    
    # 设置生产环境
    os.environ['ENVIRONMENT'] = 'production'
    os.environ['SERVER_BASE_URL'] = 'http://42.193.230.145'
    
    print("✅ 环境变量设置完成")
    print(f"   环境: {os.environ.get('ENVIRONMENT')}")
    print(f"   服务器地址: {os.environ.get('SERVER_BASE_URL')}")

def update_config_file():
    """更新配置文件"""
    print("\n=== 更新配置文件 ===")
    
    config_content = '''# 邮件服务配置
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 587
SENDER_EMAIL = "1208155205@qq.com"
SENDER_PASSWORD = "tscvmzpbazgbbaeh"

# 服务器配置
SERVER_BASE_URL = "http://42.193.230.145"  # 生产环境服务器地址
LOCAL_BASE_URL = "http://localhost:8000"    # 本地开发地址

# 根据环境变量选择服务器地址
import os
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
'''
    
    try:
        with open('app/config.py', 'w', encoding='utf-8') as f:
            f.write(config_content)
        print("✅ 配置文件更新完成")
    except Exception as e:
        print(f"❌ 配置文件更新失败: {e}")

def test_email_service():
    """测试邮件服务"""
    print("\n=== 测试邮件服务 ===")
    
    try:
        from app.services import EmailService
        from app.config import BASE_URL
        
        email_service = EmailService()
        print(f"✅ 邮件服务初始化成功")
        print(f"   服务器地址: {BASE_URL}")
        
        # 测试邮件模板
        test_url = "/memorial/test123"
        html_content = email_service._build_email_html(
            "测试宠物", 
            test_url, 
            "活泼型", 
            "这是一封测试信件"
        )
        
        if "http://42.193.230.145" in html_content:
            print("✅ 邮件模板中的服务器地址正确")
        else:
            print("❌ 邮件模板中的服务器地址不正确")
            
    except Exception as e:
        print(f"❌ 邮件服务测试失败: {e}")

def main():
    """主函数"""
    print("开始配置服务器地址...")
    print("=" * 50)
    
    # 设置环境变量
    set_environment_variables()
    
    # 更新配置文件
    update_config_file()
    
    # 测试邮件服务
    test_email_service()
    
    print("\n" + "=" * 50)
    print("=== 配置完成 ===")
    print("现在邮件中的纪念馆地址将使用生产环境服务器地址")
    print("服务器地址: http://42.193.230.145")

if __name__ == "__main__":
    main()
