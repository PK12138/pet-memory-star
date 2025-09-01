# 邮箱验证码和密码重置功能

## 功能概述

本系统已集成完整的邮箱验证码发送和密码重置功能，用户可以通过邮箱验证码安全地重置密码。

## 功能特性

### 🔐 邮箱验证码
- **6位数字验证码**：随机生成，10分钟有效期
- **防重复发送**：60秒倒计时，防止频繁请求
- **自动清理**：验证成功后自动删除验证码
- **安全验证**：验证码过期后自动失效

### 🔑 密码重置
- **邮箱验证**：通过邮箱验证码确认身份
- **安全重置**：验证成功后重置密码
- **密码加密**：使用盐值和SHA256哈希加密
- **自动跳转**：重置成功后自动跳转到登录页面

## 技术实现

### 数据库表结构

#### 1. 邮箱验证码表 (email_codes)
```sql
CREATE TABLE email_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    code TEXT NOT NULL,
    type TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. 密码重置令牌表 (password_reset_tokens)
```sql
CREATE TABLE password_reset_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    token TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### API接口

#### 1. 发送验证码
```
POST /api/auth/send-verification-code
Content-Type: application/json

{
    "email": "user@example.com"
}
```

**响应示例：**
```json
{
    "success": true,
    "message": "验证码已发送到您的邮箱"
}
```

#### 2. 重置密码
```
POST /api/auth/reset-password
Content-Type: application/json

{
    "email": "user@example.com",
    "verification_code": "123456",
    "new_password": "newpassword123"
}
```

**响应示例：**
```json
{
    "success": true,
    "message": "密码重置成功"
}
```

### 页面路由

#### 忘记密码页面
```
GET /forgot-password
```

## 邮件模板

### 验证码邮件
- **主题**：🔐 宠忆星·云纪念馆 - 邮箱验证码
- **内容**：包含6位验证码、有效期提醒、安全警告
- **样式**：美观的HTML模板，支持响应式设计

### 密码重置邮件
- **主题**：🔑 宠忆星·云纪念馆 - 密码重置
- **内容**：包含重置链接、安全提醒
- **样式**：专业的HTML模板

## 安全特性

### 🔒 验证码安全
- **随机生成**：每次生成不同的6位数字
- **时间限制**：10分钟有效期
- **一次性使用**：验证成功后立即删除
- **防暴力破解**：限制发送频率

### 🔐 密码安全
- **盐值加密**：每个用户使用唯一盐值
- **SHA256哈希**：密码不可逆加密
- **长度验证**：密码至少6位
- **格式验证**：邮箱格式验证

## 使用流程

### 1. 用户操作流程
1. 点击登录页面的"忘记密码？"链接
2. 输入注册邮箱地址
3. 点击"发送验证码"按钮
4. 检查邮箱，获取6位验证码
5. 输入验证码和新密码
6. 点击"重置密码"完成重置

### 2. 系统处理流程
1. 验证邮箱格式和用户存在性
2. 生成6位随机验证码
3. 发送验证码邮件
4. 验证用户输入的验证码
5. 重置用户密码
6. 返回成功消息

## 配置说明

### 邮件服务配置
系统使用QQ邮箱SMTP服务，配置如下：

```python
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 587
SENDER_EMAIL = "1208155205@qq.com"
SENDER_PASSWORD = "tscvmzpbazgbbaeh"  # 授权码
```

### 环境变量配置
可以通过环境变量覆盖默认配置：

```bash
export SMTP_SERVER="smtp.qq.com"
export SMTP_PORT="587"
export SENDER_EMAIL="your_email@qq.com"
export SENDER_PASSWORD="your_authorization_code"
```

## 测试方法

### 1. 启动服务器
```bash
python start_server.py
```

### 2. 运行测试脚本
```bash
python test_email_verification.py
```

### 3. 手动测试
1. 访问 `http://localhost:8000/login`
2. 点击"忘记密码？"链接
3. 输入测试邮箱
4. 发送验证码
5. 检查邮箱获取验证码
6. 完成密码重置

## 错误处理

### 常见错误及解决方案

#### 1. 验证码发送失败
- **原因**：邮件服务配置错误
- **解决**：检查SMTP配置和授权码

#### 2. 验证码验证失败
- **原因**：验证码错误或已过期
- **解决**：重新发送验证码

#### 3. 邮箱不存在
- **原因**：用户未注册
- **解决**：先注册账户

#### 4. 密码重置失败
- **原因**：数据库操作失败
- **解决**：检查数据库连接和权限

## 注意事项

### ⚠️ 安全提醒
1. **验证码保密**：不要将验证码告诉他人
2. **及时使用**：验证码10分钟内有效
3. **安全密码**：设置强密码，避免简单密码
4. **定期更换**：建议定期更换密码

### 🔧 维护建议
1. **定期清理**：清理过期的验证码和令牌
2. **监控日志**：监控邮件发送日志
3. **备份数据**：定期备份用户数据
4. **更新配置**：及时更新邮件服务配置

## 扩展功能

### 未来可添加的功能
1. **短信验证码**：支持手机短信验证
2. **双因素认证**：增加额外的安全验证
3. **登录历史**：记录用户登录历史
4. **安全提醒**：异常登录提醒
5. **密码强度检测**：实时检测密码强度

---

**开发团队**：宠忆星·云纪念馆开发组  
**最后更新**：2025年8月29日  
**版本**：v1.0.0
