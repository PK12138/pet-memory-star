#!/bin/bash

# 宠忆星·云纪念馆 - 快速修复脚本
# Pet Memory Star - Quick Fix Script

echo "🚀 快速修复部署..."

# 设置项目目录 - 使用当前目录
PROJECT_DIR="/var/www/pet-memory-sta"

# 检查当前目录
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ 项目目录不存在: $PROJECT_DIR"
    echo "当前目录: $(pwd)"
    echo "请确认您在正确的项目目录中"
    exit 1
fi

# 进入项目目录
cd $PROJECT_DIR

# 拉取最新代码
echo "⬇️ 拉取最新代码..."
git fetch origin
git reset --hard origin/main

# 设置脚本权限
echo "🔧 设置脚本权限..."
chmod +x *.sh 2>/dev/null
chmod +x *.py 2>/dev/null

# 重启服务
echo "🔄 重启服务..."
pkill -f "python.*start_server.py"
sleep 2
nohup python start_server.py > app.log 2>&1 &

echo "✅ 修复完成！"
echo "📊 服务地址: http://localhost"
echo "📋 查看日志: tail -f app.log"
