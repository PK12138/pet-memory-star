# 宠忆星·云纪念馆

一个温馨的宠物纪念网站，让爱永恒。

## 🚀 快速开始

### 本地运行
```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务器
python start_server.py
```

访问：http://localhost:8000

## 📁 项目结构

```
Pet_Memory_Star/
├── app/                          # 应用核心代码
│   ├── database.py              # 数据库操作
│   ├── main.py                  # FastAPI主程序
│   ├── services.py              # 业务逻辑
│   ├── personality_service.py   # 性格测试服务
│   ├── pet_memorials.db         # SQLite数据库
│   └── templates/               # HTML模板
│       ├── index.html           # 首页
│       ├── memorial.html        # 纪念馆页面
│       ├── personality_test.html # 性格测试页面
│       ├── reminder_setup.html  # 提醒设置页面
│       └── email_config.html    # 邮件配置页面
├── storage/                     # 文件存储
│   ├── downloads/               # 下载文件
│   ├── memorials/              # 纪念馆HTML文件
│   ├── photos/                 # 上传的照片
│   ├── portraits/              # 肖像图片
│   └── qrcodes/               # 二维码文件
├── requirements.txt            # Python依赖
├── start_server.py            # 启动脚本
├── email_config.md           # 邮件配置说明
└── README.md                 # 项目说明
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

## 🚀 部署说明

详细的云服务器部署教程请联系开发者获取。

---

**让爱永恒，让回忆温暖** ❤️
