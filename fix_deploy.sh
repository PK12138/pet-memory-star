#!/bin/bash
# 修复部署脚本 - 强制拉取最新代码

echo "=========================================="
echo "🔧 修复部署问题"
echo "=========================================="

cd /opt/pet-memory-star || exit 1

echo ""
echo "[INFO] 当前状态..."
git status

echo ""
echo "[INFO] 保存当前更改..."
git stash

echo ""
echo "[INFO] 强制重置到远程分支..."
git fetch --all
git reset --hard origin/main

echo ""
echo "[INFO] 查看最新提交..."
git log --oneline -3

echo ""
echo "[INFO] 停止旧进程..."
pkill -f uvicorn

echo ""
echo "[INFO] 激活虚拟环境并启动服务..."
cd /opt/pet-memory-star
source venv/bin/activate

echo ""
echo "[INFO] 安装/更新依赖..."
pip install -r requirements.txt --quiet

echo ""
echo "[INFO] 启动服务..."
nohup python3 start_server.py > server.log 2>&1 &

echo ""
echo "[INFO] 等待5秒..."
sleep 5

echo ""
echo "[INFO] 验证服务状态..."
curl -s http://localhost:80/api/health || echo "❌ 80端口失败，尝试443端口..."
curl -s -k https://localhost:443/api/health || echo "❌ 443端口也失败"

echo ""
echo "[INFO] 查看进程状态..."
ps aux | grep uvicorn | grep -v grep

echo ""
echo "[INFO] 查看端口监听..."
ss -tulpn | grep -E ":80|:443"

echo ""
echo "[INFO] 查看最新日志..."
tail -30 server.log

echo ""
echo "=========================================="
echo "✅ 修复完成！"
echo "=========================================="

