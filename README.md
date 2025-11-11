# 爪迹星·云纪念馆

每一颗星星，都留下了爱的爪迹。

## 🌟 项目信息

- **线上地址**: http://pettrailstar.cn
- **服务器IP**: 42.193.230.145
- **小程序AppID**: wx9572f66945407446
- **技术栈**: FastAPI + 微信小程序 + SQLite

## 🚀 快速开始

### 方式1：使用微信小程序（推荐）

1. 打开微信开发者工具
2. 导入项目：`miniprogram` 目录
3. 配置说明：查看 [小程序配置完成.md](./小程序配置完成.md)

### 方式2：Web 端访问

直接访问：http://pettrailstar.cn

### 方式3：本地开发

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动本地服务器（端口 8000）
python start_local.py

# 3. 浏览器访问
# http://localhost:8000
```

## 📁 项目结构

```
pet-memory-star/
├── app/                    # 后端核心代码
│   ├── main.py            # FastAPI 主程序
│   ├── database.py        # 数据库操作
│   ├── services.py        # 业务逻辑
│   ├── payment_service.py # 支付服务
│   └── templates/         # HTML 模板
├── miniprogram/           # 微信小程序 ✅
│   ├── pages/            # 小程序页面
│   ├── config/           # 配置文件
│   └── utils/            # 工具类
├── storage/              # 文件存储
│   ├── photos/          # 照片
│   ├── memorials/       # 纪念馆
│   └── qrcodes/         # 二维码
├── start_local.py       # 本地启动（端口 8000）
├── start_server.py      # 生产启动（端口 80）
└── 文档/
    ├── README.md                # 本文档
    ├── 小程序配置完成.md         # 配置说明 ✅
    ├── 项目整理说明.md           # 项目整理
    ├── FEATURE_SUMMARY.md       # 功能总结
    ├── DEPLOYMENT.md            # 部署指南
    └── PAYMENT_SETUP.md         # 支付集成
```

## ✨ 主要功能

- 🏠 **纪念馆创建**: 为宠物创建个性化纪念页面
- 🧠 **性格测试**: 分析宠物性格特征
- 📷 **照片轮播**: 展示宠物美好回忆
- 💌 **访客留言**: 朋友们的温暖祝福
- 🎨 **多种主题**: 个性化页面样式
- 📅 **纪念日提醒**: 重要日期提醒
- 📖 **心情日记**: 记录思念心情
- 📊 **访问统计**: 纪念馆访问数据
- 📱 **社交分享**: 分享到社交平台

## 🛠️ 技术栈

- **后端**: FastAPI + SQLite
- **前端**: HTML + CSS + JavaScript
- **模板引擎**: Jinja2
- **文件上传**: Python-multipart
- **二维码**: qrcode

## 📧 邮件配置

请参考 `email_config.md` 文件配置邮件服务。

## 📚 文档导航

- 📱 **[小程序配置完成](./小程序配置完成.md)** - 小程序已配置好，可直接使用
- 📖 **[项目整理说明](./项目整理说明.md)** - 完整项目结构和使用指南
- 🚀 **[部署指南](./DEPLOYMENT.md)** - 服务器部署详细步骤
- ✨ **[功能总结](./FEATURE_SUMMARY.md)** - 已实现功能列表
- 💰 **[支付集成](./PAYMENT_SETUP.md)** - 微信/支付宝支付配置

## 🧪 测试工具

```bash
# 测试服务器连接
python test_server_connection.py

# 测试支付功能
python test_payment.py

# 检查数据库状态
python check_database.py
```

## 🔧 常见问题

### 1. 小程序登录失败？

查看：[小程序配置完成.md](./小程序配置完成.md) 中的"常见问题"章节

### 2. 缺少依赖包？

```bash
# 安装核心依赖
pip install -r requirements.txt

# 安装支付依赖（可选）
pip install -r requirements_payment.txt
```

### 3. 需要本地调试？

查看：[miniprogram/本地开发说明.md](./miniprogram/本地开发说明.md)

## 🌐 服务器信息

- **域名**: http://pettrailstar.cn ✅ 已部署
- **服务器**: 42.193.230.145
- **项目路径**: /opt/pet-memory-star
- **HTTP端口**: 8000
- **HTTPS端口**: 443（待配置SSL证书）

---

**让爱永恒，让回忆温暖** ❤️

**版本**: 1.0.0 | **最后更新**: 2025-01-14
