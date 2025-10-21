#!/bin/bash
# 修复数据库结构问题
# 警告：此操作会删除所有数据！

echo "=========================================="
echo "🔧 数据库修复脚本"
echo "=========================================="
echo ""
echo "⚠️  警告：此操作将删除所有数据库数据！"
echo ""
read -p "确认继续？(yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ 操作已取消"
    exit 0
fi

cd /opt/pet-memory-star || exit 1

echo ""
echo "=== 1. 停止服务 ==="
pkill -f start_server.py
pkill -f uvicorn
sleep 2
echo "✅ 服务已停止"

echo ""
echo "=== 2. 备份旧数据库 ==="
if [ -f "storage/memorial_site.db" ]; then
    timestamp=$(date +%Y%m%d_%H%M%S)
    cp storage/memorial_site.db "storage/memorial_site.db.backup_$timestamp"
    echo "✅ 已备份到: storage/memorial_site.db.backup_$timestamp"
fi

echo ""
echo "=== 3. 删除旧数据库 ==="
rm -f storage/memorial_site.db
echo "✅ 旧数据库已删除"

echo ""
echo "=== 4. 启动服务（将自动创建新数据库）==="
source venv/bin/activate
nohup python3 start_server.py > app.log 2>&1 &
echo "✅ 服务已启动"

echo ""
echo "=== 5. 等待启动（10秒）==="
sleep 10

echo ""
echo "=== 6. 检查服务状态 ==="
if ps aux | grep -v grep | grep "python.*start_server.py" > /dev/null; then
    echo "✅ 服务运行正常"
else
    echo "❌ 服务未运行，查看日志："
    tail -20 app.log
    exit 1
fi

echo ""
echo "=== 7. 检查数据库 ==="
if [ -f "storage/memorial_site.db" ]; then
    echo "✅ 新数据库已创建"
    ls -lh storage/memorial_site.db
else
    echo "❌ 数据库未创建"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ 数据库修复完成！"
echo "=========================================="
echo ""
echo "📝 注意事项："
echo "   - 所有旧数据已删除"
echo "   - 需要重新注册用户"
echo "   - 备份文件位于 storage/ 目录"
echo ""

