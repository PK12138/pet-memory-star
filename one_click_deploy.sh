#!/bin/bash

# 宠忆星·云纪念馆 - 一键部署脚本
# Pet Memory Star - One Click Deployment Script

echo "🚀 开始一键部署宠忆星·云纪念馆..."

# 设置变量
PROJECT_DIR="/var/www/pet-memory-star"
GIT_REPO="https://github.com/PK12138/pet-memory-star.git"

# 创建网站目录
mkdir -p /var/www

# 检查项目是否已存在
if [ -d "$PROJECT_DIR" ]; then
    echo "📁 项目已存在，更新代码..."
    cd $PROJECT_DIR
    
    # 备份当前版本
    echo "📦 备份当前版本..."
    cp -r . ../pet-memory-star-backup-$(date +%Y%m%d_%H%M%S) 2>/dev/null
    
    # 拉取最新代码
    echo "⬇️ 拉取最新代码..."
    git fetch origin
    git reset --hard origin/main
    
    if [ $? -ne 0 ]; then
        echo "❌ 代码拉取失败，尝试重新克隆..."
        cd ..
        rm -rf pet-memory-star
        git clone $GIT_REPO
        cd pet-memory-star
    fi
else
    echo "📁 项目不存在，克隆新项目..."
    cd /var/www
    git clone $GIT_REPO
    cd pet-memory-star
fi

# 给脚本执行权限
chmod +x deploy.sh
chmod +x quick_deploy.sh

# 运行快速部署
echo "🔄 运行快速部署..."
./quick_deploy.sh

echo "🎉 一键部署完成！"
echo "📊 服务地址: http://localhost:8000"
