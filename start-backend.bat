@echo off
echo ========================================
echo   爪迹星后端服务器启动脚本
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] 检查Python环境...
python --version
if errorlevel 1 (
    echo 错误：未找到Python，请先安装Python
    pause
    exit /b 1
)

echo.
echo [2/3] 安装依赖...
pip install -r "%~dp0\requirements.txt" -q
if errorlevel 1 (
    echo 警告：依赖安装失败，继续尝试启动...
)

echo.
echo [3/3] 启动服务器...
echo 服务器地址: http://localhost:8000
echo 按 Ctrl+C 停止服务器
echo.

python start_local.py

pause


