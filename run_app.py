#!/usr/bin/env python3
"""
宠忆星·云纪念馆启动脚本
"""

import os
import sys
import uvicorn

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 设置环境变量
os.environ['ENVIRONMENT'] = 'production'
os.environ['SERVER_BASE_URL'] = 'http://42.193.230.145'

def main():
    """主函数"""
    print("🚀 启动宠忆星·云纪念馆服务...")
    print(f"📍 服务地址: http://localhost")
    print(f"📖 API文档: http://localhost/docs")
    print(f"📁 当前目录: {project_root}")
    print(f"📁 App目录: {os.path.join(project_root, 'app')}")
    
    # 启动服务器
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=80,
        reload=True,
        reload_dirs=[project_root]
    )

if __name__ == "__main__":
    main()
