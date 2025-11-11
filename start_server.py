#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 爪迹星·云纪念馆启动脚本
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

import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
