# 🔒 HTTPS配置完整指南

## 📋 概述

将 `http://pettrailstar.cn` 升级为 `https://pettrailstar.cn`

**优势：**
- ✅ 微信小程序必须使用HTTPS
- ✅ 数据传输加密，更安全
- ✅ 浏览器不再显示"不安全"警告
- ✅ SEO排名更好

---

## 方案选择

### 方案一：云服务商免费SSL证书（推荐）⭐

**优点：**
- 完全免费
- 自动续期
- 配置简单
- 阿里云/腾讯云都支持

**缺点：**
- 需要域名备案

### 方案二：Let's Encrypt 免费证书

**优点：**
- 完全免费
- 自动化程度高
- 全球通用

**缺点：**
- 需要手动续期（可以设置自动续期脚本）

---

## 🎯 推荐方案：阿里云免费SSL证书

### Step 1: 申请免费SSL证书

#### 1.1 登录阿里云控制台

访问：https://www.aliyun.com/
- 登录您的账号
- 进入控制台

#### 1.2 进入SSL证书服务

**导航路径：**
```
产品与服务 → 安全 → SSL证书（应用安全）
```

或直接访问：https://yundun.console.aliyun.com/?p=cas

#### 1.3 购买免费证书

1. 点击"SSL证书" → "免费证书"
2. 选择"DV单域名证书（免费试用）"
3. 点击"立即购买"（价格：0元）
4. 确认订单

#### 1.4 创建证书

1. 在"SSL证书"页面，点击"创建证书"
2. 填写域名信息：
   - **证书绑定域名**：`pettrailstar.cn` 或 `*.pettrailstar.cn`（泛域名需要付费）
   - **域名验证方式**：自动DNS验证（推荐）
   - **联系人**：填写您的信息

3. 点击"提交审核"

#### 1.5 验证域名所有权

**DNS验证（自动）：**
- 阿里云会自动在您的域名DNS中添加TXT记录
- 如果域名在阿里云，自动验证
- 如果域名不在阿里云，需要手动添加DNS记录

**等待审核：**
- 通常5-30分钟
- 审核通过后状态变为"已签发"

#### 1.6 下载证书

1. 找到已签发的证书
2. 点击"下载"
3. 选择服务器类型：**Nginx** 或 **Apache**
4. 下载证书压缩包

证书包含两个文件：
- `域名.pem` - 证书文件
- `域名.key` - 私钥文件

---

## 🔧 Step 2: 在服务器上配置HTTPS

### 2.1 安装Nginx（如果未安装）

```bash
# SSH连接服务器
ssh root@42.193.230.145

# 安装Nginx
yum install -y nginx

# 启动Nginx
systemctl start nginx
systemctl enable nginx

# 检查Nginx状态
systemctl status nginx
```

### 2.2 上传SSL证书到服务器

**在本地电脑执行：**

```bash
# 创建证书目录（在服务器上）
ssh root@42.193.230.145 "mkdir -p /etc/nginx/ssl"

# 上传证书文件（替换为您实际的证书文件名）
scp pettrailstar.cn.pem root@42.193.230.145:/etc/nginx/ssl/
scp pettrailstar.cn.key root@42.193.230.145:/etc/nginx/ssl/

# 设置权限
ssh root@42.193.230.145 "chmod 600 /etc/nginx/ssl/*"
```

### 2.3 配置Nginx

SSH连接服务器后，创建Nginx配置：

```bash
# 编辑Nginx配置
vim /etc/nginx/conf.d/pettrailstar.conf
```

**配置内容：**

```nginx
# HTTP服务器 - 自动跳转到HTTPS
server {
    listen 80;
    server_name pettrailstar.cn www.pettrailstar.cn;
    
    # 自动重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

# HTTPS服务器
server {
    listen 443 ssl http2;
    server_name pettrailstar.cn www.pettrailstar.cn;
    
    # SSL证书配置
    ssl_certificate /etc/nginx/ssl/pettrailstar.cn.pem;
    ssl_certificate_key /etc/nginx/ssl/pettrailstar.cn.key;
    
    # SSL优化配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # 安全头部
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    # 上传大小限制
    client_max_body_size 50M;
    
    # 代理到后端FastAPI服务
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持（如果需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # 静态文件
    location /static/ {
        alias /root/pet-memory-star/app/static/;
        expires 30d;
    }
    
    location /uploads/ {
        alias /root/pet-memory-star/app/uploads/;
        expires 30d;
    }
}
```

### 2.4 测试并重启Nginx

```bash
# 测试配置文件语法
nginx -t

# 如果测试通过，重启Nginx
systemctl restart nginx

# 查看Nginx状态
systemctl status nginx

# 查看错误日志（如果有问题）
tail -f /var/log/nginx/error.log
```

### 2.5 开放443端口

```bash
# 如果使用firewalld
firewall-cmd --permanent --add-service=https
firewall-cmd --reload

# 如果使用iptables
iptables -I INPUT -p tcp --dport 443 -j ACCEPT
service iptables save

# 阿里云安全组
# 需要在阿里云控制台添加安全组规则：
# 入方向 → 添加规则 → 443端口 → 允许
```

**阿里云安全组配置：**
1. 登录阿里云控制台
2. 进入 ECS 实例
3. 点击"安全组" → "配置规则"
4. 添加入方向规则：
   - 端口范围：443/443
   - 授权对象：0.0.0.0/0
   - 描述：HTTPS

---

## 📱 Step 3: 修改小程序代码

### 3.1 更新API基础地址

**修改 `miniprogram/utils/api.js`：**

```javascript
// utils/api.js
const config = {
  baseUrl: 'https://pettrailstar.cn'  // ✅ 改为HTTPS
  // baseUrl: 'http://42.193.230.145'  // ❌ 旧的HTTP地址
}
```

**修改 `miniprogram/app.js`：**

```javascript
// app.js
globalData: {
  baseUrl: 'https://pettrailstar.cn',  // ✅ 改为HTTPS
  sessionToken: null,
  userInfo: null
}
```

### 3.2 配置小程序服务器域名

1. 登录微信公众平台：https://mp.weixin.qq.com
2. 进入"开发" → "开发管理" → "开发设置"
3. 找到"服务器域名"
4. 配置以下域名：

```
request合法域名：
https://pettrailstar.cn

uploadFile合法域名：
https://pettrailstar.cn

downloadFile合法域名：
https://pettrailstar.cn
```

**注意：**
- 域名必须是HTTPS
- 域名必须备案
- 每月只能修改5次
- 修改后立即生效

---

## 🧪 Step 4: 测试HTTPS

### 4.1 命令行测试

```bash
# 测试HTTPS连接
curl https://pettrailstar.cn/api/health

# 查看证书信息
openssl s_client -connect pettrailstar.cn:443 -servername pettrailstar.cn
```

### 4.2 浏览器测试

1. 访问：https://pettrailstar.cn
2. 查看地址栏是否显示🔒图标
3. 点击🔒查看证书信息

### 4.3 在线SSL检测

访问：https://www.ssllabs.com/ssltest/
- 输入：`pettrailstar.cn`
- 点击"Submit"
- 等待检测完成
- 评分应该是A或A+

### 4.4 小程序测试

1. 修改代码中的API地址
2. 编译小程序
3. 点击"预览"
4. 用手机扫码测试
5. 查看控制台是否有HTTPS相关错误

---

## 🔄 证书续期

### 阿里云免费证书

**有效期：** 1年

**续期方式：**
1. 证书到期前1个月，阿里云会发送提醒
2. 重新申请免费证书
3. 下载新证书
4. 替换服务器上的证书文件
5. 重启Nginx

**自动化脚本（可选）：**

```bash
#!/bin/bash
# /root/scripts/renew-ssl.sh

# 备份旧证书
cp /etc/nginx/ssl/pettrailstar.cn.pem /etc/nginx/ssl/pettrailstar.cn.pem.bak
cp /etc/nginx/ssl/pettrailstar.cn.key /etc/nginx/ssl/pettrailstar.cn.key.bak

# 上传新证书（手动执行）
# scp 新证书 root@服务器:/etc/nginx/ssl/

# 重启Nginx
nginx -t && systemctl reload nginx

echo "SSL证书已更新"
```

---

## ⚠️ 常见问题

### ❌ 问题1：证书不受信任

**原因：**
- 证书未正确安装
- 证书链不完整

**解决：**
```bash
# 检查证书
openssl x509 -in /etc/nginx/ssl/pettrailstar.cn.pem -text -noout

# 确保pem文件包含完整证书链
cat 域名.pem 中间证书.pem > fullchain.pem
```

### ❌ 问题2：Nginx启动失败

**原因：**
- 配置文件语法错误
- 证书文件路径错误
- 端口被占用

**解决：**
```bash
# 检查语法
nginx -t

# 查看错误日志
tail -f /var/log/nginx/error.log

# 检查443端口
netstat -tlnp | grep 443
```

### ❌ 问题3：小程序请求失败

**原因：**
- 域名未在微信后台配置
- 域名未备案
- 证书问题

**解决：**
1. 检查微信公众平台的服务器域名配置
2. 确认域名已备案
3. 测试HTTPS是否正常：`curl https://pettrailstar.cn/api/health`

### ❌ 问题4：HTTP自动跳转不生效

**原因：**
- Nginx配置未生效

**解决：**
```bash
# 重启Nginx
systemctl restart nginx

# 清除浏览器缓存
# 使用无痕模式测试
```

---

## 📊 完整配置检查清单

### 服务器端
- [ ] SSL证书已申请并下载
- [ ] Nginx已安装
- [ ] 证书文件已上传到服务器
- [ ] Nginx配置文件已创建
- [ ] Nginx配置测试通过
- [ ] Nginx已重启
- [ ] 443端口已开放
- [ ] 阿里云安全组已配置

### 域名端
- [ ] 域名已备案
- [ ] DNS已正确解析到服务器IP
- [ ] HTTPS可以正常访问

### 小程序端
- [ ] API地址已改为HTTPS
- [ ] 微信后台已配置服务器域名
- [ ] 小程序可以正常请求API
- [ ] 无SSL相关错误

### 测试验证
- [ ] 浏览器访问显示🔒
- [ ] SSL Labs评分A级以上
- [ ] 小程序真机测试通过
- [ ] HTTP自动跳转HTTPS

---

## 🚀 快速执行命令汇总

```bash
# 1. 安装Nginx
yum install -y nginx

# 2. 创建证书目录
mkdir -p /etc/nginx/ssl

# 3. 上传证书（在本地执行）
scp 证书.pem root@42.193.230.145:/etc/nginx/ssl/
scp 证书.key root@42.193.230.145:/etc/nginx/ssl/

# 4. 创建Nginx配置
vim /etc/nginx/conf.d/pettrailstar.conf
# （粘贴上面的配置内容）

# 5. 测试并重启
nginx -t
systemctl restart nginx

# 6. 开放443端口
firewall-cmd --permanent --add-service=https
firewall-cmd --reload

# 7. 测试HTTPS
curl https://pettrailstar.cn/api/health
```

---

## 📝 下一步

配置完成后：

1. ✅ 修改小程序代码中的API地址
2. ✅ 在微信后台配置服务器域名
3. ✅ 提交代码并发布新版本
4. ✅ 设置证书到期提醒
5. ✅ 定期检查SSL证书状态

---

**需要帮助？**

- 阿里云SSL证书文档：https://help.aliyun.com/product/28533.html
- Nginx官方文档：https://nginx.org/en/docs/
- 微信小程序服务器域名配置：https://developers.weixin.qq.com/miniprogram/dev/framework/ability/network.html


