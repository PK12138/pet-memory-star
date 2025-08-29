# 🚀 宠忆星·云纪念馆 - 部署指南

## 📋 目录
- [服务器环境要求](#服务器环境要求)
- [手动部署](#手动部署)
- [自动化部署](#自动化部署)
- [Windows部署](#windows部署)
- [Docker部署](#docker部署)
- [故障排除](#故障排除)

## 🖥️ 服务器环境要求

### 基础要求
- **操作系统**: Linux (Ubuntu 18.04+) / Windows Server 2016+
- **Python**: 3.8+
- **内存**: 最少 1GB RAM
- **存储**: 最少 2GB 可用空间

### 必需软件
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip git nginx

# CentOS/RHEL
sudo yum install python3 python3-pip git nginx
```

## 🔧 手动部署

### 1. 克隆项目
```bash
# 进入网站目录
cd /var/www

# 克隆项目
git clone https://github.com/PK12138/pet-memory-star.git
cd pet-memory-star
```

### 2. 安装依赖
```bash
# 安装Python依赖
pip3 install -r requirements.txt

# 或者使用虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 配置环境变量
```bash
# 复制环境变量模板
cp env_example.txt .env

# 编辑配置文件
nano .env
```

### 4. 启动服务
```bash
# 直接启动
python3 start_server.py

# 后台运行
nohup python3 start_server.py > app.log 2>&1 &
```

## 🤖 自动化部署

### 一键部署（推荐）
```bash
# Linux服务器
chmod +x one_click_deploy.sh
./one_click_deploy.sh

# Windows服务器
one_click_deploy.bat
```

### 分步部署

#### Linux服务器
```bash
# 给脚本执行权限
chmod +x deploy.sh

# 运行完整部署脚本
./deploy.sh

# 或运行快速部署脚本
./quick_deploy.sh
```

#### Windows服务器
```cmd
# 运行Windows部署脚本
deploy.bat
```

## 🐳 Docker部署

### 1. 构建镜像
```bash
docker build -t pet-memory-star .
```

### 2. 运行容器
```bash
docker run -d \
  --name pet-memory-star \
  -p 8000:8000 \
  -v /var/www/pet-memory-star/storage:/app/storage \
  pet-memory-star
```

### 3. 使用Docker Compose
```bash
# 创建docker-compose.yml
version: '3.8'
services:
  pet-memory-star:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./storage:/app/storage
    environment:
      - DEBUG=False
    restart: unless-stopped
```

## 🔄 更新部署

### 方法1: 使用部署脚本
```bash
# Linux
./deploy.sh

# Windows
deploy.bat
```

### 方法2: 手动更新
```bash
# 进入项目目录
cd /var/www/pet-memory-star

# 拉取最新代码
git fetch origin
git reset --hard origin/main

# 重启服务
pkill -f "python.*start_server.py"
nohup python3 start_server.py > app.log 2>&1 &
```

## 🔍 服务管理

### 检查服务状态
```bash
# 检查进程
ps aux | grep python

# 检查端口
netstat -tlnp | grep 8000

# 检查日志
tail -f app.log
```

### 停止服务
```bash
# 查找并杀死进程
pkill -f "python.*start_server.py"

# 或者使用进程ID
kill -9 <PID>
```

## 🛠️ 故障排除

### 常见问题

#### 1. 端口被占用
```bash
# 查看端口占用
lsof -i :8000

# 杀死占用进程
kill -9 <PID>
```

#### 2. 权限问题
```bash
# 修改目录权限
sudo chown -R www-data:www-data /var/www/pet-memory-star
sudo chmod -R 755 /var/www/pet-memory-star
```

#### 3. 依赖安装失败
```bash
# 升级pip
pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

#### 4. 数据库连接失败
```bash
# 检查数据库配置
cat app/config.py

# 测试数据库连接
python3 -c "from app.database import init_db; init_db()"
```

### 日志查看
```bash
# 应用日志
tail -f app.log

# 系统日志
tail -f /var/log/syslog

# Nginx日志
tail -f /var/log/nginx/access.log
```

## 📞 技术支持

如果遇到问题，请：

1. 查看日志文件
2. 检查配置文件
3. 确认网络连接
4. 联系技术支持

---

**注意**: 部署前请确保已备份重要数据！
