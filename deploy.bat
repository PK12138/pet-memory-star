@echo off
chcp 65001 >nul
echo 🚀 开始部署宠忆星·云纪念馆...

:: 设置项目目录（请根据实际情况修改）
set PROJECT_DIR=D:\www\pet-memory-star

:: 进入项目目录
cd /d %PROJECT_DIR%

:: 拉取最新代码
echo ⬇️ 拉取最新代码...
git fetch origin
git reset --hard origin/main

:: 停止旧服务
echo 🔄 停止旧服务...
taskkill /f /im python.exe 2>nul
timeout /t 2 /nobreak >nul

:: 启动新服务
echo 🚀 启动新服务...
start /b python start_server.py

echo ✅ 部署完成！
echo 📊 服务地址: http://localhost:8000
pause
