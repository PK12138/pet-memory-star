#!/bin/bash

#  爪迹星·云纪念馆部署脚本
# 用于在云服务器上更新代码并重启服务

echo "🚀 开始部署 爪迹星·云纪念馆到云服务器..."

# 服务器信息
SERVER_IP="42.193.230.145"
SERVER_USER="root"
PROJECT_DIR="/root/pet-memory-star"

echo "📡 连接到服务器: $SERVER_IP"

# 1. 连接到服务器并更新代码
ssh $SERVER_USER@$SERVER_IP << 'EOF'
    echo "📁 进入项目目录: $PROJECT_DIR"
    cd $PROJECT_DIR
    
    echo "🔄 拉取最新代码..."
    git pull origin main
    
    echo "📦 安装/更新依赖..."
    pip install -r requirements.txt
    
    echo "🔧 设置环境变量..."
    export ENVIRONMENT=production
    export SERVER_BASE_URL=http://42.193.230.145
    
    echo "🛑 停止现有服务..."
    pkill -f "uvicorn.*main:app" || true
    
    echo "⏳ 等待服务停止..."
    sleep 3
    
    echo "🚀 启动新服务..."
    nohup python run_app.py > app.log 2>&1 &
    
    echo "⏳ 等待服务启动..."
    sleep 5
    
    echo "🔍 检查服务状态..."
    if pgrep -f "uvicorn.*main:app" > /dev/null; then
        echo "✅ 服务启动成功"
        echo "📊 服务进程信息:"
        ps aux | grep "uvicorn.*main:app" | grep -v grep
        echo "📝 最新日志:"
        tail -10 app.log
    else
        echo "❌ 服务启动失败"
        echo "📝 错误日志:"
        tail -20 app.log
    fi
    
    echo "🌐 检查端口状态..."
    netstat -tlnp | grep :80
EOF

echo "✅ 部署完成！"
echo "📍 服务地址: http://$SERVER_IP"
echo "📖 API文档: http://$SERVER_IP/docs"
