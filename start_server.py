#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
宠忆星·云纪念馆启动脚本
"""

import uvicorn
import os
import sys

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ 环境变量加载成功")
except ImportError:
    print("⚠️  python-dotenv未安装，环境变量可能无法正确加载")
except Exception as e:
    print(f"⚠️  环境变量加载失败: {e}")

# 添加app目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, 'app')
sys.path.insert(0, app_dir)

if __name__ == "__main__":
    print("🚀 启动宠忆星·云纪念馆服务...")
    print("📍 服务地址: http://localhost")
    print("📖 API文档: http://localhost/docs")
    print(f"📁 当前目录: {current_dir}")
    print(f"📁 App目录: {app_dir}")
    
    # 显示邮件配置信息
    print("\n📧 邮件服务配置:")
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.qq.com')
    smtp_port = os.getenv('SMTP_PORT', '587')
    sender_email = os.getenv('SMTP_USERNAME', '1208155205@qq.com')
    sender_password = os.getenv('SMTP_PASSWORD', 'qq1208155205')
    print(f"   SMTP服务器: {smtp_server}")
    print(f"   SMTP端口: {smtp_port}")
    print(f"   发件人邮箱: {sender_email}")
    if sender_password:
        print("   ✅ 发件人密码: 已配置")
    else:
        print("   ⚠️  发件人密码: 未配置 (邮件功能将不可用)")
    print("   📖 详细配置请查看 email_config.md 文件")
    print("   🧪 可以运行 python test_email.py 测试邮件功能")
    print()
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=80,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
