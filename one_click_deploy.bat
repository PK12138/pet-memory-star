@echo off
chcp 65001 >nul
echo 🚀 开始一键部署宠忆星·云纪念馆...

:: 设置变量
set PROJECT_DIR=D:\www\pet-memory-star
set GIT_REPO=https://github.com/PK12138/pet-memory-star.git

:: 创建网站目录
if not exist "D:\www" mkdir "D:\www"

:: 检查项目是否已存在
if exist "%PROJECT_DIR%" (
    echo 📁 项目已存在，更新代码...
    cd /d "%PROJECT_DIR%"
    
    :: 备份当前版本
    echo 📦 备份当前版本...
    xcopy . "..\pet-memory-star-backup-%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%" /E /I /Y >nul 2>&1
    
    :: 拉取最新代码
    echo ⬇️ 拉取最新代码...
    git fetch origin
    git reset --hard origin/main
    
    if errorlevel 1 (
        echo ❌ 代码拉取失败，尝试重新克隆...
        cd /d "D:\www"
        rmdir /s /q pet-memory-star
        git clone %GIT_REPO%
        cd pet-memory-star
    )
) else (
    echo 📁 项目不存在，克隆新项目...
    cd /d "D:\www"
    git clone %GIT_REPO%
    cd pet-memory-star
)

:: 运行Windows部署脚本
echo 🔄 运行Windows部署脚本...
call deploy.bat

echo 🎉 一键部署完成！
echo 📊 服务地址: http://localhost
pause
