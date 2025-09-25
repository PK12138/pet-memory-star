# 网络问题诊断指南

## 问题现象
- API请求超时：`request:fail timeout`
- 重试机制触发但最终失败
- 注册功能无法正常工作

## 诊断步骤

### 1. 检查服务器状态
```bash
# 在项目根目录运行
cd Test/Pet_Memory_Star
python3 start_local.py
```

### 2. 测试健康检查接口
访问：`http://localhost:8000/api/health`
应该返回：
```json
{
  "status": "healthy",
  "message": "服务器运行正常",
  "timestamp": "2025-09-18T13:36:23Z"
}
```

### 3. 使用小程序网络诊断页面
1. 在微信开发者工具中打开小程序
2. 导航到：`pages/network-test/network-test`
3. 点击"开始诊断"按钮
4. 查看诊断结果和修复建议

### 4. 检查配置文件
确认 `miniprogram/config/config.js` 中的 `baseUrl` 设置：
- 本地开发：`http://localhost:8000`
- 生产环境：`https://pettrailstar.cn`

## 常见问题及解决方案

### 问题1：服务器未启动
**现象**：所有API请求都超时
**解决**：
1. 确保在项目根目录运行 `python3 start_local.py`
2. 检查端口8000是否被占用
3. 查看控制台是否有错误信息

### 问题2：域名无法访问
**现象**：生产环境API请求超时
**解决**：
1. 检查域名解析：`nslookup pettrailstar.cn`
2. 确认服务器正在运行
3. 检查防火墙设置

### 问题3：HTTPS证书问题
**现象**：HTTPS请求失败
**解决**：
1. 检查SSL证书是否有效
2. 确认证书链完整
3. 测试证书：`openssl s_client -connect pettrailstar.cn:443`

### 问题4：小程序域名配置
**现象**：小程序无法访问API
**解决**：
1. 在微信公众平台添加合法域名
2. 确保域名支持HTTPS
3. 检查TLS版本兼容性

## 测试命令

### 本地测试
```bash
# 启动本地服务器
python3 start_local.py

# 测试健康检查
curl http://localhost:8000/api/health

# 测试注册接口
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"123456","confirm_password":"123456"}'
```

### 生产环境测试
```bash
# 测试健康检查
curl https://pettrailstar.cn/api/health

# 测试HTTPS证书
openssl s_client -connect pettrailstar.cn:443 -servername pettrailstar.cn
```

## 配置切换

### 切换到本地开发
1. 修改 `miniprogram/config/config.js`：
   ```javascript
   baseUrl: 'http://localhost:8000'
   ```

### 切换到生产环境
1. 修改 `miniprogram/config/config.js`：
   ```javascript
   baseUrl: 'https://pettrailstar.cn'
   ```

## 监控和日志

### 服务器日志
查看控制台输出的详细日志，包括：
- 请求接收时间
- 处理时间
- 错误信息

### 小程序日志
在微信开发者工具中查看：
- 网络请求日志
- 错误堆栈信息
- 重试次数和间隔

## 联系支持

如果问题仍然存在，请提供：
1. 完整的错误日志
2. 网络诊断结果
3. 服务器状态截图
4. 小程序版本信息
