#!/bin/bash

echo "=========================================="
echo "🚑 一键诊断和修复脚本"
echo "=========================================="
echo ""

# 进入项目目录
cd /opt/pet-memory-star || { echo "❌ 项目目录不存在"; exit 1; }

echo "=== 1. 检查当前进程状态 ==="
CURRENT_PROCESS=$(ps aux | grep "python3 start_server.py" | grep -v grep)
if [ -n "$CURRENT_PROCESS" ]; then
    echo "✅ 发现运行中的进程："
    echo "$CURRENT_PROCESS"
else
    echo "⚠️ 服务未运行"
fi
echo ""

echo "=== 2. 检查端口状态 ==="
PORT_80=$(ss -tulpn | grep :80)
PORT_443=$(ss -tulpn | grep :443)
if [ -n "$PORT_80" ]; then
    echo "✅ 端口80正在监听："
    echo "$PORT_80"
else
    echo "⚠️ 端口80未监听"
fi
if [ -n "$PORT_443" ]; then
    echo "✅ 端口443正在监听："
    echo "$PORT_443"
else
    echo "⚠️ 端口443未监听"
fi
echo ""

echo "=== 3. 停止所有旧进程 ==="
pkill -9 -f "python3 start_server.py"
pkill -9 -f "uvicorn"
sleep 2
echo "✅ 已清理旧进程"
echo ""

echo "=== 4. 拉取最新代码 ==="
git fetch --all
git reset --hard origin/main
echo "✅ 代码已更新到最新版本"
echo ""

echo "=== 5. 检查Python环境 ==="
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ 虚拟环境已激活"
else
    echo "❌ 虚拟环境不存在，正在创建..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi
echo ""

echo "=== 6. 检查依赖 ==="
pip list | grep -E "fastapi|uvicorn|cryptography" || pip install -r requirements.txt
echo ""

echo "=== 7. 检查数据库 ==="
if [ -f "app/pet_memorials.db" ]; then
    echo "✅ 数据库文件存在"
    # 检查表结构
    sqlite3 app/pet_memorials.db "SELECT name FROM sqlite_master WHERE type='table';" | head -5
else
    echo "⚠️ 数据库文件不存在，将在启动时自动创建"
fi
echo ""

echo "=== 8. 启动服务 ==="
nohup python3 start_server.py > nohup.out 2>&1 &
PROCESS_PID=$!
echo "✅ 服务已启动，PID: $PROCESS_PID"
echo ""

echo "=== 9. 等待服务启动... ==="
for i in {1..10}; do
    sleep 1
    if ss -tulpn | grep -q :80; then
        echo "✅ 端口80已开始监听"
        break
    fi
    echo "等待中... ($i/10)"
done
echo ""

echo "=== 10. 查看启动日志 ==="
tail -50 nohup.out
echo ""

echo "=== 11. 测试API ==="
sleep 2
echo "健康检查："
curl -s http://localhost/api/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost/api/health
echo ""

echo "=== 12. 最终状态检查 ==="
echo "进程状态："
ps aux | grep "python3 start_server.py" | grep -v grep
echo ""
echo "端口监听："
ss -tulpn | grep -E ":80|:443"
echo ""

echo "=========================================="
echo "✅ 修复完成"
echo "=========================================="
echo ""
echo "📝 下一步："
echo "1. 检查上方日志是否有错误"
echo "2. 确认端口80和443正在监听"
echo "3. 在小程序中清除缓存并重新登录"
echo ""
echo "如果仍然失败，请运行："
echo "  tail -100 nohup.out"
echo "  查看详细错误日志"

