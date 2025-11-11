#!/bin/bash
# 快速更新服务器代码并重启服务
# 使用方法: bash 快速更新服务器.sh

echo "=========================================="
echo "🚀 快速更新服务器代码"
echo "=========================================="
echo ""

# 1. 进入项目目录
cd /opt/pet-memory-star || { echo "❌ 项目目录不存在"; exit 1; }

# 2. 拉取最新代码
echo "📥 拉取最新代码..."
git fetch --all
git reset --hard origin/main
echo "✅ 代码更新完成"
echo ""

# 3. 查看最新提交
echo "📋 最新提交信息:"
git log -1 --oneline
echo ""

# 4. 停止旧服务
echo "🛑 停止旧服务..."
pkill -f "python.*start_server.py" || echo "   (没有运行中的服务)"
pkill -f uvicorn || echo "   (没有uvicorn进程)"
sleep 2
echo ""

# 5. 激活虚拟环境并启动新服务
echo "🚀 启动新服务..."
source venv/bin/activate
nohup python3 start_server.py > nohup.out 2>&1 &
echo "✅ 服务已在后台启动"
echo ""

# 6. 等待服务启动
echo "⏳ 等待服务启动 (10秒)..."
sleep 10
echo ""

# 7. 检查服务状态
echo "🔍 检查服务状态:"
if ps aux | grep -v grep | grep -q "python.*start_server.py"; then
    echo "   ✅ 服务进程运行正常"
    PID=$(ps aux | grep -v grep | grep "python.*start_server.py" | awk '{print $2}' | head -1)
    echo "   进程ID: $PID"
else
    echo "   ❌ 服务未运行，请检查日志"
    echo ""
    echo "查看日志: tail -50 /opt/pet-memory-star/nohup.out"
    exit 1
fi
echo ""

# 8. 检查端口监听
echo "🔌 检查端口监听:"
if ss -tulpn | grep -q ":80"; then
    echo "   ✅ 端口 80 正在监听"
else
    echo "   ⚠️  端口 80 未监听"
fi
echo ""

# 9. 测试 API
echo "🧪 测试 API 端点:"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/)
if [ "$RESPONSE" = "200" ]; then
    echo "   ✅ 首页访问正常 (HTTP $RESPONSE)"
else
    echo "   ⚠️  首页访问异常 (HTTP $RESPONSE)"
fi
echo ""

# 10. 显示最近日志
echo "📄 最近日志 (最后20行):"
echo "----------------------------------------"
tail -20 nohup.out
echo "----------------------------------------"
echo ""

echo "=========================================="
echo "✅ 部署完成！"
echo "=========================================="
echo ""
echo "📌 有用的命令:"
echo "   查看完整日志: tail -f /opt/pet-memory-star/nohup.out"
echo "   查看进程状态: ps aux | grep python"
echo "   停止服务: pkill -f uvicorn"
echo "   查看端口: ss -tulpn | grep :80"
echo ""

