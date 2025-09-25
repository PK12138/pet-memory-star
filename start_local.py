#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动本地开发服务器
用于小程序开发和测试
"""

import os
import sys
import uvicorn

# 添加项目路径到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'app'))

if __name__ == "__main__":
    print("🚀 启动爪迹星本地开发服务器...")
    print(f"📁 项目根目录: {project_root}")
    print(f"🌐 服务器地址: http://localhost:8000")
    print(f"📖 API文档: http://localhost:8000/docs")
    print(f"🔍 健康检查: http://localhost:8000/api/health")
    print("=" * 50)
    
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            reload_dirs=[project_root],
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)
