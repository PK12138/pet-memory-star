#!/bin/bash

echo "=========================================="
echo "📋 查看服务器日志"
echo "=========================================="
echo ""

echo "=== 最近50行日志 ==="
tail -50 /opt/pet-memory-star/nohup.out

echo ""
echo "=========================================="
echo "=== 查看数据库中的会话记录 ==="
echo "=========================================="

cd /opt/pet-memory-star
sqlite3 app/pet_memorials.db << 'EOF'
.headers on
.mode column
SELECT 
    session_token as token,
    user_id,
    datetime(expires_at) as expires,
    datetime('now') as current_time,
    CASE 
        WHEN expires_at > datetime('now') THEN 'VALID'
        ELSE 'EXPIRED'
    END as status,
    datetime(created_at) as created
FROM user_sessions 
ORDER BY created_at DESC 
LIMIT 5;
EOF

echo ""
echo "=========================================="
echo "💡 如果看到会话状态为 EXPIRED，说明时区问题仍然存在"
echo "=========================================="

