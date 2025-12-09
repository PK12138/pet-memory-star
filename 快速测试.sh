#!/bin/bash
# 快速测试脚本（Linux/Mac）

echo "========================================"
echo "🚀 开始功能测试"
echo "========================================"
echo ""

cd "$(dirname "$0")"
python3 test_all_features.py http://pettrailstar.cn

echo ""
echo "========================================"
echo "📊 数据库完整性检查"
echo "========================================"
echo ""

python3 check_database_integrity.py

echo ""
echo "========================================"
echo "✅ 测试完成"
echo "========================================"

