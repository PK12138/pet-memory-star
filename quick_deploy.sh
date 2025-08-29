#!/bin/bash

# 宠忆星·云纪念馆 - 快速部署脚本
# Pet Memory Star - Quick Deployment Script

echo "🚀 快速部署宠忆星·云纪念馆..."

# 设置项目目录（请根据实际情况修改）
PROJECT_DIR="/var/www/pet-memory-star"

# 进入项目目录
cd $PROJECT_DIR

# 拉取最新代码
echo "⬇️  拉取最新代码..."
git fetch origin
git reset --hard origin/main

# 重启服务
echo "🔄 重启服务..."
pkill -f "python.*start_server.py"
sleep 2
nohup python start_server.py > app.log 2>&1 &

echo "✅ 部署完成！"
echo "📊 服务地址: http://42.193.230.145"
