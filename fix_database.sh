#!/bin/bash

echo "=== 1. 停止服务 ==="
pkill -f uvicorn

echo ""
echo "=== 2. 备份数据库 ==="
cp /opt/pet-memory-star/app/pet_memorials.db /opt/pet-memory-star/app/pet_memorials.db.bak

echo ""
echo "=== 3. 删除旧数据库 ==="
rm /opt/pet-memory-star/app/pet_memorials.db

echo ""
echo "=== 4. 启动服务（会自动创建新数据库）==="
cd /opt/pet-memory-star
source venv/bin/activate
nohup python3 start_server.py > nohup.out 2>&1 &

echo ""
echo "=== 5. 等待10秒让数据库初始化 ==="
sleep 10

echo ""
echo "=== 6. 测试API ==="
curl -s http://localhost/api/health | python3 -m json.tool || echo "健康检查失败"

echo ""
echo "=== 7. 查看服务日志 ==="
tail -n 50 nohup.out

echo ""
echo "✅ 数据库修复完成"