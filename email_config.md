# 📧 邮件服务配置说明

## 概述
宠忆星·云纪念馆系统支持自动发送邮件通知功能，当用户创建纪念馆成功后，系统会自动发送一封包含纪念馆链接的邮件。

## 配置步骤

### 1. 获取邮箱授权码

#### 163邮箱
1. 登录163邮箱
2. 进入"设置" -> "POP3/SMTP/IMAP"
3. 开启"SMTP服务"
4. 获取"授权码"（不是登录密码）

#### QQ邮箱
1. 登录QQ邮箱
2. 进入"设置" -> "账户"
3. 开启"POP3/SMTP服务"
4. 获取"授权码"

#### Gmail
1. 开启"两步验证"
2. 生成"应用专用密码"
3. 使用应用专用密码作为SENDER_PASSWORD

### 2. 配置环境变量

在项目根目录创建或编辑 `.env` 文件：

```bash
# 163邮箱配置示例
SMTP_SERVER=smtp.163.com
SMTP_PORT=587
SENDER_EMAIL=your_email@163.com
SENDER_PASSWORD=your_authorization_code

# QQ邮箱配置示例
# SMTP_SERVER=smtp.qq.com
# SMTP_PORT=587
# SENDER_EMAIL=your_email@qq.com
# SENDER_PASSWORD=your_authorization_code

# Gmail配置示例
# SMTP_SERVER=smtp.gmail.com
# SMTP_PORT=587
# SENDER_EMAIL=your_email@gmail.com
# SENDER_PASSWORD=your_app_password
```

### 3. 测试邮件服务

配置完成后，可以通过以下方式测试：

1. 启动应用
2. 创建纪念馆时填写真实邮箱
3. 检查是否收到邮件通知

## 邮件内容

系统发送的邮件包含：
- 🎯 纪念馆创建成功通知
- 🔗 纪念馆访问链接
- 🧠 性格测试结果（如果有）
- 💌 AI信件预览（如果有）
- 📱 美观的HTML格式

## 故障排除

### 常见问题

1. **邮件发送失败**
   - 检查SMTP服务器和端口是否正确
   - 确认授权码是否正确
   - 检查网络连接

2. **163邮箱问题**
   - 确保开启了SMTP服务
   - 使用授权码而不是登录密码

3. **QQ邮箱问题**
   - 确保开启了POP3/SMTP服务
   - 使用授权码而不是QQ密码

4. **Gmail问题**
   - 确保开启了两步验证
   - 使用应用专用密码

### 调试方法

在应用启动时，系统会打印邮件配置信息：
```
📧 邮件服务配置:
   SMTP服务器: smtp.163.com
   SMTP端口: 587
   发件人邮箱: your_email@163.com
```

## 安全提醒

1. **不要将授权码提交到代码仓库**
2. **使用环境变量或配置文件存储敏感信息**
3. **定期更换授权码**
4. **限制邮件发送频率，避免被识别为垃圾邮件**

## 支持的服务商

- ✅ 163邮箱
- ✅ QQ邮箱
- ✅ Gmail
- ✅ 其他支持SMTP的邮箱服务商

## 联系支持

如果遇到配置问题，请检查：
1. 邮箱服务商设置
2. 网络连接
3. 防火墙设置
4. 应用日志输出
