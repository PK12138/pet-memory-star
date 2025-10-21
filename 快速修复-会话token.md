# 🔧 会话Token问题修复

## 问题分析

**根本原因：前后端请求头不匹配**

- **前端**（小程序）发送：`Authorization: Bearer <token>`
- **后端**（API）期望：`x-session-token: <token>`

导致后端无法识别用户会话，返回"用户未登录"错误。

## 修复内容

### 1. 修改小程序API请求头

**文件：** `miniprogram/utils/api.js`

```javascript
// 修改前
header: {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${app.globalData.sessionToken}`,
  ...header
}

// 修改后
header: {
  'Content-Type': 'application/json',
  'x-session-token': app.globalData.sessionToken || '',
  ...header
}
```

### 2. 增强登录状态持久化

**文件：** `miniprogram/app.js`

- 启动时自动从本地存储恢复登录状态
- 登录时同步保存到全局数据和本地存储
- 登出时彻底清除所有登录信息
- 添加详细的日志记录

## 部署步骤

### 在服务器上执行：

```bash
cd /opt/pet-memory-star
git fetch --all
git reset --hard origin/main
pkill -f python3
source venv/bin/activate
nohup python3 start_server.py > nohup.out 2>&1 &
sleep 3
tail -50 nohup.out
```

### 测试步骤：

1. **清除小程序缓存**
   - 开发者工具 → 清除缓存
   - 重新编译

2. **测试登录流程**
   - 登录账号
   - 检查首页是否正常加载数据
   - 点击"我的纪念馆"
   - 确认能看到纪念馆列表

3. **测试创建纪念馆**
   - 创建新的纪念馆
   - 填写宠物信息
   - 提交后检查是否成功创建
   - 返回列表页，确认新纪念馆显示

## 预期结果

✅ 登录成功后不再显示"登录失败"提示
✅ 首页API调用成功，显示用户等级和统计信息
✅ 纪念馆列表正常加载
✅ 页面切换保持登录状态
✅ 重启小程序后保持登录状态

## 诊断工具

如果问题仍然存在，在服务器上运行诊断脚本：

```bash
bash /opt/pet-memory-star/服务器诊断.sh
```

这将检查：
- 数据库中的会话记录
- API请求日志
- 服务器进程状态
- 端口监听状态

## 相关提交

- `50d9963`: Fix: Improve login state persistence in mini-program
- `985ad72`: Fix: Use correct session token header (x-session-token) for API requests

