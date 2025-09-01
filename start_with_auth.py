#!/usr/bin/env python3
"""
带用户认证系统的启动脚本
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# 添加app目录到Python路径
app_dir = os.path.join(os.path.dirname(__file__), "app")
sys.path.insert(0, app_dir)

# 加载环境变量
load_dotenv()

def main():
    """主启动函数"""
    print("🚀 启动宠忆星·云纪念馆服务（带用户认证系统）...")
    print(f"📍 服务地址: http://localhost:8000")
    print(f"📖 API文档: http://localhost:8000/docs")
    print(f"📁 当前目录: {os.getcwd()}")
    print(f"📁 App目录: {app_dir}")
    
    # 检查必要的目录
    storage_dir = os.path.join(os.path.dirname(__file__), "storage")
    if not os.path.exists(storage_dir):
        os.makedirs(storage_dir)
        print(f"✅ 创建存储目录: {storage_dir}")
    
    # 创建必要的子目录
    subdirs = ["photos", "memorials", "downloads", "qrcodes"]
    for subdir in subdirs:
        subdir_path = os.path.join(storage_dir, subdir)
        if not os.path.exists(subdir_path):
            os.makedirs(subdir_path)
            print(f"✅ 创建子目录: {subdir_path}")
    
    # 启动服务器
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
