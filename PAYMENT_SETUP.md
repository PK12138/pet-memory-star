# 支付功能集成指南

本指南详细说明如何集成微信支付和支付宝支付功能。

## 1. 环境准备

### 1.1 安装依赖

```bash
pip install -r requirements_payment.txt
```

### 1.2 创建证书目录

```bash
mkdir -p certs
chmod 700 certs
```

## 2. 微信支付集成

### 2.1 申请微信支付商户号

1. 访问 [微信支付商户平台](https://pay.weixin.qq.com/)
2. 注册并完成企业认证
3. 获取以下信息：
   - 商户号 (mch_id)
   - API密钥 (api_key)
   - 应用ID (app_id)

### 2.2 配置微信支付

1. 下载API证书：
   - 登录商户平台
   - 进入"账户中心" -> "API安全"
   - 下载API证书

2. 将证书文件放入 `certs/` 目录：
   ```
   certs/
   ├── wechat_private_key.pem  # 商户私钥
   └── wechat_cert.pem         # 商户证书
   ```

3. 设置环境变量：
   ```bash
   export WECHAT_APP_ID="your_app_id"
   export WECHAT_MCH_ID="your_merchant_id"
   export WECHAT_API_KEY="your_api_key"
   export WECHAT_CERT_SERIAL_NO="your_cert_serial_no"
   export WECHAT_PRIVATE_KEY_PATH="certs/wechat_private_key.pem"
   export WECHAT_CERT_PATH="certs/wechat_cert.pem"
   export WECHAT_NOTIFY_URL="https://yourdomain.com/api/payment/wechat/notify"
   ```

### 2.3 微信支付流程

1. 用户选择微信支付
2. 前端获取用户openid
3. 后端调用微信支付API创建订单
4. 前端调用微信支付JS-SDK完成支付
5. 微信支付回调通知支付结果

## 3. 支付宝集成

### 3.1 申请支付宝应用

1. 访问 [支付宝开放平台](https://open.alipay.com/)
2. 创建应用并完成认证
3. 获取以下信息：
   - 应用ID (app_id)
   - 应用私钥
   - 支付宝公钥

### 3.2 配置支付宝

1. 生成密钥对：
   ```bash
   # 生成私钥
   openssl genrsa -out alipay_private_key.pem 2048
   
   # 生成公钥
   openssl rsa -in alipay_private_key.pem -pubout -out alipay_public_key.pem
   ```

2. 将密钥文件放入 `certs/` 目录：
   ```
   certs/
   ├── alipay_private_key.pem   # 应用私钥
   └── alipay_public_key.pem    # 应用公钥
   ```

3. 设置环境变量：
   ```bash
   export ALIPAY_APP_ID="your_app_id"
   export ALIPAY_PRIVATE_KEY_PATH="certs/alipay_private_key.pem"
   export ALIPAY_PUBLIC_KEY_PATH="certs/alipay_public_key.pem"
   export ALIPAY_NOTIFY_URL="https://yourdomain.com/api/payment/alipay/notify"
   export ALIPAY_RETURN_URL="https://yourdomain.com/payment/success"
   export ALIPAY_SANDBOX="true"  # 沙箱环境，生产环境设为false
   ```

### 3.3 支付宝支付流程

1. 用户选择支付宝支付
2. 后端调用支付宝API创建订单
3. 前端跳转到支付宝支付页面
4. 用户完成支付后返回
5. 支付宝异步通知支付结果

## 4. 环境变量配置

创建 `.env.payment` 文件：

```bash
# 微信支付配置
WECHAT_APP_ID=your_wechat_app_id
WECHAT_MCH_ID=your_merchant_id
WECHAT_API_KEY=your_api_key
WECHAT_CERT_SERIAL_NO=your_cert_serial_no
WECHAT_PRIVATE_KEY_PATH=certs/wechat_private_key.pem
WECHAT_CERT_PATH=certs/wechat_cert.pem
WECHAT_NOTIFY_URL=https://yourdomain.com/api/payment/wechat/notify

# 支付宝配置
ALIPAY_APP_ID=your_alipay_app_id
ALIPAY_PRIVATE_KEY_PATH=certs/alipay_private_key.pem
ALIPAY_PUBLIC_KEY_PATH=certs/alipay_public_key.pem
ALIPAY_NOTIFY_URL=https://yourdomain.com/api/payment/alipay/notify
ALIPAY_RETURN_URL=https://yourdomain.com/payment/success
ALIPAY_SANDBOX=true

# 服务器配置
SERVER_BASE_URL=https://yourdomain.com
```

## 5. 测试支付功能

### 5.1 微信支付测试

1. 使用微信开发者工具或微信内置浏览器
2. 访问支付页面
3. 选择微信支付
4. 完成支付流程

### 5.2 支付宝测试

1. 设置 `ALIPAY_SANDBOX=true` 使用沙箱环境
2. 访问支付页面
3. 选择支付宝支付
4. 使用沙箱账号完成支付

## 6. 生产环境部署

### 6.1 安全配置

1. 确保证书文件权限：
   ```bash
   chmod 600 certs/*.pem
   ```

2. 使用HTTPS：
   - 支付回调必须使用HTTPS
   - 确保证书有效

3. 环境变量：
   - 生产环境使用真实配置
   - 设置 `ALIPAY_SANDBOX=false`

### 6.2 监控和日志

1. 监控支付成功率
2. 记录支付日志
3. 设置异常告警

## 7. 常见问题

### 7.1 微信支付问题

- **签名验证失败**：检查证书和密钥配置
- **openid获取失败**：确保在微信环境中调用
- **支付失败**：检查商户号和API密钥

### 7.2 支付宝问题

- **签名验证失败**：检查密钥配置
- **沙箱测试失败**：使用沙箱账号和测试金额
- **回调验证失败**：检查回调URL配置

## 8. 开发调试

### 8.1 本地调试

1. 使用ngrok等工具暴露本地服务
2. 配置回调URL为ngrok地址
3. 在支付平台配置回调地址

### 8.2 日志调试

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 9. 安全建议

1. **证书安全**：
   - 定期更新证书
   - 使用强密码保护私钥
   - 限制证书文件访问权限

2. **API安全**：
   - 验证支付回调签名
   - 使用HTTPS传输
   - 限制API访问频率

3. **数据安全**：
   - 加密敏感数据
   - 定期备份数据
   - 监控异常交易

## 10. 扩展功能

1. **退款功能**：实现订单退款
2. **分账功能**：支持多商户分账
3. **对账功能**：自动对账和结算
4. **风控功能**：交易风险控制
