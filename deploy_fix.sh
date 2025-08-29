#!/bin/bash

# 宠忆星·云纪念馆 - 修正部署脚本
# Pet Memory Star - Fixed Deployment Script

echo "🚀 开始部署宠忆星·云纪念馆..."

# 设置变量 - 根据实际目录调整
PROJECT_DIR="/var/www/pet-memory-sta"  # 修正为实际目录名
BACKUP_DIR="/var/backups/pet-memory-sta"
LOG_FILE="/var/log/pet-memory-sta/deploy.log"

# 创建日志目录
mkdir -p /var/log/pet-memory-sta

# 记录部署开始时间
echo "$(date): 开始部署" >> $LOG_FILE

# 1. 检查项目目录是否存在
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ 项目目录不存在: $PROJECT_DIR"
    echo "请检查目录路径或先克隆项目"
    exit 1
fi

# 2. 备份当前版本
echo "📦 备份当前版本..."
if [ -d "$PROJECT_DIR" ]; then
    mkdir -p $BACKUP_DIR
    cp -r $PROJECT_DIR $BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S)
    echo "$(date): 备份完成" >> $LOG_FILE
fi

# 3. 进入项目目录
cd $PROJECT_DIR

# 4. 检查Git状态
echo "🔍 检查Git状态..."
git status

# 5. 拉取最新代码
echo "⬇️ 拉取最新代码..."
git fetch origin
git reset --hard origin/main

# 6. 检查拉取结果
if [ $? -eq 0 ]; then
    echo "✅ 代码拉取成功"
    echo "$(date): 代码拉取成功" >> $LOG_FILE
else
    echo "❌ 代码拉取失败"
    echo "$(date): 代码拉取失败" >> $LOG_FILE
    exit 1
fi

# 7. 给脚本执行权限
echo "🔧 设置脚本权限..."
chmod +x *.sh 2>/dev/null
chmod +x *.py 2>/dev/null

# 8. 安装/更新依赖
echo "📦 更新Python依赖..."
pip install -r requirements.txt

# 9. 重启服务
echo "🔄 重启服务..."

# 查找并杀死旧进程
pkill -f "python.*start_server.py"

# 启动新服务
cd $PROJECT_DIR
nohup python start_server.py > app.log 2>&1 &
echo "✅ 服务启动成功"
echo "$(date): 服务启动成功" >> $LOG_FILE

# 10. 检查服务状态
echo "🔍 检查服务状态..."
sleep 3

if curl -s http://localhost > /dev/null; then
    echo "✅ 服务运行正常"
    echo "$(date): 服务运行正常" >> $LOG_FILE
else
    echo "❌ 服务可能未正常启动，请检查日志"
    echo "$(date): 服务启动异常" >> $LOG_FILE
fi

# 11. 清理旧备份（保留最近5个）
echo "🧹 清理旧备份..."
cd $BACKUP_DIR
ls -t | tail -n +6 | xargs -r rm -rf

echo "🎉 部署完成！"
echo "$(date): 部署完成" >> $LOG_FILE

# 显示部署信息
echo ""
echo "📊 部署信息："
echo "   项目目录: $PROJECT_DIR"
echo "   备份目录: $BACKUP_DIR"
echo "   日志文件: $LOG_FILE"
echo "   服务地址: http://your-server-ip"
echo ""
