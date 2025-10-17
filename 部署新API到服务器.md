# 🚀 部署新API到服务器

## 📋 部署步骤

### 方法一：使用Git（推荐）

#### 1. 提交本地代码
```bash
# 在本地 D:\code\pet-memory-star
cd D:\code\pet-memory-star

# 查看修改的文件
git status

# 添加修改的文件
git add app/main.py

# 提交
git commit -m "添加小程序创建纪念馆API /api/memorial/create"

# 推送到远程仓库
git push
```

#### 2. SSH登录服务器
```bash
ssh root@42.193.230.145
```

#### 3. 拉取最新代码
```bash
cd /opt/pet-memory-star

# 拉取最新代码
git pull origin main
# 或者
git pull origin master
```

#### 4. 重启服务
```bash
# 查找正在运行的进程
ps aux | grep uvicorn

# 输出示例：
# root     12345  0.5  2.3  xxxxxx  xxxxx ? S    10:00   0:30 python start_server.py

# 杀掉旧进程（使用上面找到的进程ID）
kill -9 12345

# 或者一键杀掉所有uvicorn进程
pkill -9 -f uvicorn

# 重新启动服务
cd /opt/pet-memory-star
source venv/bin/activate
nohup python start_server.py > server.log 2>&1 &

# 查看日志确认启动成功
tail -f server.log
```

---

### 方法二：直接上传文件（快速方法）

#### 1. 使用SFTP/SCP上传文件

**使用WinSCP或FileZilla**：
1. 连接到 `42.193.230.145`
2. 导航到 `/opt/pet-memory-star/app/`
3. 上传 `main.py` 文件覆盖服务器上的旧文件

**使用命令行SCP**：
```bash
# 在本地PowerShell中执行
scp D:\code\pet-memory-star\app\main.py root@42.193.230.145:/opt/pet-memory-star/app/main.py
```

#### 2. SSH登录并重启服务
```bash
ssh root@42.193.230.145

# 重启服务
cd /opt/pet-memory-star
pkill -9 -f uvicorn
source venv/bin/activate
nohup python start_server.py > server.log 2>&1 &

# 查看日志
tail -f server.log
```

---

### 方法三：使用部署脚本

#### 1. 创建部署脚本（如果还没有）

在本地创建 `deploy_api_update.sh`：

```bash
#!/bin/bash

echo "🚀 开始部署新API到服务器..."

# 服务器信息
SERVER_USER="root"
SERVER_IP="42.193.230.145"
SERVER_PATH="/opt/pet-memory-star"

# 上传更新的文件
echo "📤 上传 main.py..."
scp app/main.py ${SERVER_USER}@${SERVER_IP}:${SERVER_PATH}/app/main.py

# SSH到服务器并重启
echo "🔄 重启服务器..."
ssh ${SERVER_USER}@${SERVER_IP} << 'EOF'
cd /opt/pet-memory-star

# 杀掉旧进程
echo "⏹️  停止旧服务..."
pkill -9 -f uvicorn

# 等待进程完全停止
sleep 2

# 启动新服务
echo "▶️  启动新服务..."
source venv/bin/activate
nohup python start_server.py > server.log 2>&1 &

# 等待服务启动
sleep 3

# 检查服务状态
if pgrep -f uvicorn > /dev/null; then
    echo "✅ 服务启动成功！"
    echo "📊 查看最新日志："
    tail -20 server.log
else
    echo "❌ 服务启动失败！"
    echo "📋 错误日志："
    tail -50 server.log
fi
EOF

echo "🎉 部署完成！"
```

#### 2. 运行部署脚本
```bash
# 给脚本执行权限
chmod +x deploy_api_update.sh

# 执行部署
./deploy_api_update.sh
```

---

## ✅ 验证部署

### 1. 检查服务状态

SSH登录服务器后：
```bash
# 检查进程是否运行
ps aux | grep uvicorn

# 查看最新日志
tail -50 /opt/pet-memory-star/server.log

# 实时查看日志
tail -f /opt/pet-memory-star/server.log
```

### 2. 测试新API

```bash
# 方法1：使用curl（在服务器上）
curl http://localhost:8000/api/health

# 方法2：使用curl测试新API（需要token）
# 先登录获取token，然后：
curl -X POST http://42.193.230.145/api/memorial/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"pet_name":"测试","breed":"测试品种","age":"3","gender":"公","description":"测试"}'
```

### 3. 从小程序测试

1. **清除小程序缓存**：
   - 微信开发者工具 → 工具 → 清除缓存 → 清除全部

2. **重新编译**

3. **测试流程**：
   - 登录
   - 进入性格测试
   - 完成测试
   - 点击"创建纪念馆"
   - **查看Console日志**：应该看到 `200 OK` 而不是 `404`

---

## 🔍 常见问题

### 问题1：上传文件失败

**可能原因**：
- SSH密钥未配置
- 防火墙阻止

**解决**：
```bash
# 使用密码登录
scp -o PreferredAuthentications=password app/main.py root@42.193.230.145:/opt/pet-memory-star/app/
```

### 问题2：服务启动失败

**检查日志**：
```bash
tail -100 /opt/pet-memory-star/server.log
```

**常见错误**：
- 端口被占用：`kill -9` 所有Python进程后重试
- Python环境问题：检查 `venv` 是否激活
- 语法错误：检查 `main.py` 是否有语法错误

### 问题3：API仍然404

**检查**：
```bash
# 确认文件已更新
cat /opt/pet-memory-star/app/main.py | grep "api/memorial/create"

# 应该看到：
# @app.post("/api/memorial/create")
```

**解决**：
- 确认文件已成功上传
- 确认服务已重启
- 检查nginx配置（如果使用）

---

## 📊 部署检查清单

- [ ] 本地代码已修改并测试
- [ ] 使用Git提交或直接上传 `main.py`
- [ ] SSH登录服务器成功
- [ ] 代码已更新到服务器
- [ ] 旧服务进程已停止
- [ ] 新服务已启动
- [ ] 日志显示正常启动
- [ ] API健康检查通过
- [ ] 小程序可以成功创建纪念馆

---

## 🎯 快速部署命令（推荐）

如果你熟悉命令行，可以一键执行：

```bash
# 上传文件并重启服务（一条命令）
scp app/main.py root@42.193.230.145:/opt/pet-memory-star/app/main.py && \
ssh root@42.193.230.145 "cd /opt/pet-memory-star && pkill -9 -f uvicorn && sleep 2 && source venv/bin/activate && nohup python start_server.py > server.log 2>&1 & sleep 3 && tail -20 server.log"
```

---

## 📝 注意事项

1. **备份**：部署前建议备份服务器上的 `main.py`：
   ```bash
   ssh root@42.193.230.145
   cp /opt/pet-memory-star/app/main.py /opt/pet-memory-star/app/main.py.backup
   ```

2. **测试环境**：如果可能，先在测试环境验证再部署到生产环境

3. **回滚准备**：如果部署失败，可以快速回滚：
   ```bash
   cp /opt/pet-memory-star/app/main.py.backup /opt/pet-memory-star/app/main.py
   pkill -9 -f uvicorn
   cd /opt/pet-memory-star && source venv/bin/activate
   nohup python start_server.py > server.log 2>&1 &
   ```

4. **Nginx配置**：如果使用Nginx反向代理，确保配置正确转发到8000端口

---

**✨ 选择最适合你的方法部署，建议使用"快速部署命令"最简单！**

_创建时间: 2025-01-14_

