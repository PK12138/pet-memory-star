#!/bin/bash

echo "=========================================="
echo "🔄 重启宠忆星服务"
echo "=========================================="
echo ""

cd /opt/pet-memory-star

echo "=== 1. 拉取最新代码 ==="
git fetch --all
git reset --hard origin/main
echo ""

echo "=== 2. 停止旧服务 ==="
pkill -f "python3 start_server.py"
pkill -f "uvicorn"
sleep 2
echo ""

echo "=== 3. 启动新服务 ==="
source venv/bin/activate
nohup python3 start_server.py > nohup.out 2>&1 &
sleep 3
echo ""

echo "=== 4. 检查服务状态 ==="
echo "进程状态："
ps aux | grep "python3 start_server.py" | grep -v grep || echo "⚠️ 服务未运行"
echo ""

echo "端口监听："
ss -tulpn | grep :80 || echo "⚠️ 端口80未监听"
echo ""

echo "=== 5. 查看启动日志 ==="
tail -30 nohup.out
echo ""

echo "=== 6. 测试API ==="
sleep 2
curl -s http://localhost/api/health | python3 -m json.tool || echo "⚠️ API测试失败"
echo ""

echo "=========================================="
echo "✅ 重启完成"
echo "=========================================="

