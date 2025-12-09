@echo off
chcp 65001 >nul
echo ========================================
echo 🚀 开始功能测试
echo ========================================
echo.

cd /d %~dp0
python test_all_features.py http://pettrailstar.cn

echo.
echo ========================================
echo 📊 数据库完整性检查
echo ========================================
echo.

python check_database_integrity.py

echo.
echo ========================================
echo ✅ 测试完成
echo ========================================
pause

