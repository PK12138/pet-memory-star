# 爪迹星小程序部署指南

## 📱 小程序信息

- **AppID**: `wx9572f66945407446`
- **AppSecret**: `c4b410be644231ff5635ec960dde38c1`
- **项目名称**: 爪迹星·云纪念馆

## 🚀 部署步骤

### 第一步：配置后端API

1. **修改API地址**
   ```javascript
   // 在 config/config.js 中修改
   baseUrl: 'https://yourdomain.com', // 替换为你的实际域名
   ```

2. **配置CORS**
   确保后端API支持小程序的跨域请求：
   ```python
   # 在 main.py 中添加
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],  # 生产环境建议指定具体域名
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

### 第二步：配置微信小程序

1. **登录微信公众平台**
   - 访问 [微信公众平台](https://mp.weixin.qq.com/)
   - 使用AppID: `wx9572f66945407446` 登录

2. **配置服务器域名**
   在"开发" → "开发管理" → "开发设置" → "服务器域名"中添加：
   
   **request合法域名**：
   ```
   https://yourdomain.com
   ```
   
   **uploadFile合法域名**：
   ```
   https://yourdomain.com
   ```
   
   **downloadFile合法域名**：
   ```
   https://yourdomain.com
   ```

3. **配置业务域名**
   在"开发" → "开发管理" → "开发设置" → "业务域名"中添加：
   ```
   yourdomain.com
   ```

### 第三步：开发环境测试

1. **安装微信开发者工具**
   - 下载 [微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)
   - 安装并登录

2. **导入项目**
   - 打开微信开发者工具
   - 选择"导入项目"
   - 选择 `miniprogram` 目录
   - 输入AppID: `wx9572f66945407446`
   - 点击"导入"

3. **本地调试**
   - 点击"编译"按钮
   - 在模拟器中测试功能
   - 使用"真机调试"在手机上测试

### 第四步：上传和发布

1. **上传代码**
   - 在微信开发者工具中点击"上传"
   - 填写版本号（如：1.0.0）
   - 填写项目备注
   - 点击"上传"

2. **提交审核**
   - 登录微信公众平台
   - 进入"管理" → "版本管理"
   - 找到上传的版本，点击"提交审核"
   - 填写审核信息

3. **发布上线**
   - 审核通过后，点击"发布"
   - 确认发布信息
   - 完成上线

## 🔧 配置说明

### 1. 项目配置 (project.config.json)
```json
{
  "appid": "wx9572f66945407446",
  "projectname": "爪迹星·云纪念馆"
}
```

### 2. 应用配置 (config/config.js)
```javascript
module.exports = {
  appId: 'wx9572f66945407446',
  appSecret: 'c4b410be644231ff5635ec960dde38c1',
  baseUrl: 'https://yourdomain.com'
}
```

### 3. 全局配置 (app.js)
```javascript
globalData: {
  appId: 'wx9572f66945407446',
  appSecret: 'c4b410be644231ff5635ec960dde38c1',
  baseUrl: 'https://yourdomain.com'
}
```

## 🛠️ 开发工具

### 1. 微信开发者工具
- 版本：最新稳定版
- 功能：代码编辑、调试、上传、发布

### 2. 调试功能
- **模拟器调试**: 在电脑上模拟小程序运行
- **真机调试**: 在手机上实时调试
- **远程调试**: 通过微信开发者工具远程调试

### 3. 性能分析
- **性能面板**: 分析页面性能
- **内存面板**: 监控内存使用
- **网络面板**: 查看网络请求

## 📊 监控和维护

### 1. 数据统计
- 用户访问量
- 功能使用情况
- 错误日志分析

### 2. 版本管理
- 版本号规范：主版本.次版本.修订版本
- 更新日志记录
- 回滚机制

### 3. 安全监控
- API调用频率限制
- 用户行为异常检测
- 数据安全保护

## 🚨 常见问题

### 1. 网络请求失败
**问题**: 小程序无法访问后端API
**解决**: 
- 检查服务器域名是否在合法域名列表中
- 确认后端API支持HTTPS
- 检查CORS配置

### 2. 登录功能异常
**问题**: 用户无法正常登录
**解决**:
- 检查session_token是否正确传递
- 确认后端登录接口返回格式
- 检查用户权限验证逻辑

### 3. 图片上传失败
**问题**: 照片无法上传
**解决**:
- 检查文件大小限制（小程序限制10MB）
- 确认上传接口支持multipart/form-data
- 检查图片格式是否支持

### 4. 支付功能异常
**问题**: 微信支付无法使用
**解决**:
- 确认小程序已开通微信支付
- 检查支付参数配置
- 确认商户号和密钥正确

## 📞 技术支持

如有问题，请联系开发团队：
- 邮箱：support@example.com
- 微信：your_wechat_id
- 电话：your_phone_number

---

⭐ 每一颗星星，都留下了爱的爪迹 ⭐
