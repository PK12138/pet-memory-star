#!/bin/bash

echo "================================"
echo "🔧 诊断并修复服务器问题"
echo "================================"

# 1. 检查Python环境
echo ""
echo "1. 检查Python环境..."
which python
python --version
which python3
python3 --version

# 2. 检查虚拟环境
echo ""
echo "2. 检查虚拟环境..."
ls -la /opt/pet-memory-star/venv/bin/

# 3. 检查start_server.py
echo ""
echo "3. 检查start_server.py..."
ls -la /opt/pet-memory-star/start_server.py

# 4. 检查当前进程
echo ""
echo "4. 检查是否有运行的服务..."
ps aux | grep -E "uvicorn|python.*start" | grep -v grep

# 5. 查看之前的错误日志
echo ""
echo "5. 查看日志（如果存在）..."
if [ -f /opt/pet-memory-star/server.log ]; then
    tail -50 /opt/pet-memory-star/server.log
else
    echo "日志文件不存在"
fi

# 6. 正确的启动方法
echo ""
echo "================================"
echo "6. 正确启动服务..."
echo "================================"

cd /opt/pet-memory-star

# 激活虚拟环境
source venv/bin/activate

# 使用完整路径启动
echo "使用venv中的python启动..."
nohup /opt/pet-memory-star/venv/bin/python start_server.py > server.log 2>&1 &

# 等待启动
sleep 5

# 7. 验证
echo ""
echo "7. 验证服务..."
ps aux | grep -E "uvicorn|python.*start" | grep -v grep

echo ""
echo "8. 测试连接..."
curl -s http://localhost:8000/api/health | head -20

echo ""
echo "9. 查看最新日志..."
tail -30 server.log

echo ""
echo "================================"
echo "✅ 诊断完成"
echo "================================"

