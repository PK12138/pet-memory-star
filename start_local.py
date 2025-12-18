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
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    print("Start local dev server...")
    print(f"Project root: {project_root}")
    print("Server: http://localhost:8000")
    print("Docs:   http://localhost:8000/docs")
    print("Health: http://localhost:8000/api/health")
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
