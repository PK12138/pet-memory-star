#!/bin/bash

echo "=========================================="
echo "🔍 服务器诊断工具"
echo "=========================================="
echo ""

echo "=== 1. 检查数据库sessions表 ==="
cd /opt/pet-memory-star
sqlite3 app/pet_memorials.db "SELECT session_id, user_id, datetime(created_at, 'unixepoch') as created, datetime(expires_at, 'unixepoch') as expires FROM sessions ORDER BY created_at DESC LIMIT 5;"

echo ""
echo "=== 2. 检查最近的API请求日志 ==="
tail -50 /opt/pet-memory-star/app.log | grep -E "(验证会话|Session|用户未登录|获取用户纪念馆列表)"

echo ""
echo "=== 3. 检查服务器进程 ==="
ps aux | grep python3 | grep -v grep

echo ""
echo "=== 4. 检查服务器端口 ==="
ss -tulpn | grep -E ":80|:443"

echo ""
echo "=== 5. 测试API端点（使用真实token） ==="
echo "请手动运行："
echo "TOKEN=\"你的sessionToken\""
echo "curl -X GET http://localhost/api/user/memorials -H \"Authorization: Bearer \$TOKEN\" -H \"Content-Type: application/json\""

