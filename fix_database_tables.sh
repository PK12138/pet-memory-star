#!/bin/bash

echo "🔧 开始修复数据库表..."

DB_PATH="app/pet_memorials.db"

# 检查数据库文件是否存在
if [ ! -f "$DB_PATH" ]; then
    echo "❌ 数据库文件不存在: $DB_PATH"
    exit 1
fi

echo "📊 检查现有表..."
sqlite3 $DB_PATH "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"

echo ""
echo "📸 检查照片相关表..."
sqlite3 $DB_PATH "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%photo%';"

echo ""
echo "🔍 检查是否存在 photos 表..."
PHOTOS_EXISTS=$(sqlite3 $DB_PATH "SELECT name FROM sqlite_master WHERE type='table' AND name='photos';" 2>/dev/null)

if [ ! -z "$PHOTOS_EXISTS" ]; then
    echo "⚠️  发现旧的 photos 表"
    PHOTOS_COUNT=$(sqlite3 $DB_PATH "SELECT COUNT(*) FROM photos;" 2>/dev/null)
    echo "📝 photos 表中有 $PHOTOS_COUNT 条记录"
fi

echo ""
echo "🔍 检查 memorial_photos 表..."
MEMORIAL_PHOTOS_EXISTS=$(sqlite3 $DB_PATH "SELECT name FROM sqlite_master WHERE type='table' AND name='memorial_photos';" 2>/dev/null)

if [ ! -z "$MEMORIAL_PHOTOS_EXISTS" ]; then
    MEMORIAL_PHOTOS_COUNT=$(sqlite3 $DB_PATH "SELECT COUNT(*) FROM memorial_photos;" 2>/dev/null)
    echo "✅ memorial_photos 表存在，有 $MEMORIAL_PHOTOS_COUNT 条记录"
else
    echo "❌ memorial_photos 表不存在"
fi

echo ""
echo "🔍 检查用户等级表..."
LEVEL_COUNT=$(sqlite3 $DB_PATH "SELECT COUNT(*) FROM user_levels;" 2>/dev/null)
echo "📝 user_levels 表中有 $LEVEL_COUNT 条记录"

if [ "$LEVEL_COUNT" -eq "0" ]; then
    echo "⚠️  用户等级表为空，插入默认数据..."
    sqlite3 $DB_PATH <<EOF
INSERT INTO user_levels (level, name, max_memorials, max_photos, can_use_ai, can_export, can_custom_domain, price_monthly, price_yearly, description)
VALUES 
(0, '免费用户', 1, 10, 0, 0, 0, 0.0, 0.0, '免费试用，创建1个纪念馆，最多10张照片'),
(1, '高级会员', -1, -1, 1, 1, 0, 29.9, 299.0, '无限纪念馆和照片，支持AI功能');
EOF
    echo "✅ 用户等级数据已插入"
fi

echo ""
echo "✅ 数据库检查完成！"
echo ""
echo "如果需要重启服务，请运行："
echo "  ./restart.sh"
echo "或："
echo "  pkill -f 'python.*start_server.py' && nohup python start_server.py > server.log 2>&1 &"





