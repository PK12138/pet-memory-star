# 爪迹星·云纪念馆 🌟

> 每一颗星星，都留下了爱的爪迹

为离世的宠物创建永恒的数字纪念空间，让爱与回忆永不消逝。

---

## 📱 在线体验

- **网页端**: http://pettrailstar.cn
- **微信小程序**: 搜索"爪迹星"（AppID: wx9572f66945407446）
- **服务器**: 42.193.230.145

---

## ✨ 核心功能

### 🏠 纪念馆系统
- **个性化纪念馆**: 为每只宠物创建专属纪念页面
- **照片轮播展示**: 保存美好回忆瞬间
- **访客留言板**: 朋友们的温暖祝福
- **社交分享**: 一键分享到微信、朋友圈

### 🎨 情感互动
- **AI对话陪伴**: 与宠物的虚拟形象对话
- **性格测试**: 深度分析宠物性格特征
- **心情日记**: 记录思念与回忆
- **梦境日记**: 记录与宠物相关的梦

### 🌈 星币系统
- **每日签到**: 连续签到获得星币奖励
- **任务奖励**: 完成互动任务赚取星币
- **星币商城**: 兑换会员、解锁高级功能

### 🎯 高级功能
- **星空纪念**: 3D星空展示所有纪念馆
- **多种主题**: 个性化页面样式
- **纪念日提醒**: 重要日期自动提醒
- **访问统计**: 纪念馆访问数据分析

---

## 🚀 快速开始

### 方式1：微信小程序（推荐）

1. 打开微信，搜索小程序"爪迹星"
2. 或使用微信开发者工具导入 `miniprogram` 目录

### 方式2：Web端访问

直接访问：http://pettrailstar.cn

### 方式3：本地开发

```bash
# 1. 克隆项目
git clone https://github.com/yourusername/pet-memory-star.git
cd pet-memory-star

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动服务器
python start_server.py

# 4. 访问应用
# Web端: http://localhost:80
```

---

## 📁 项目结构

```
pet-memory-star/
├── app/                        # 后端核心代码
│   ├── main.py                # FastAPI 主程序
│   ├── database.py            # 数据库操作
│   ├── auth_service.py        # 认证服务（微信登录）
│   ├── coins_service.py       # 星币系统
│   ├── ai_chat_service.py     # AI对话服务
│   ├── payment_service.py     # 支付服务
│   └── templates/             # HTML 模板
│       ├── landing.html       # 落地页
│       ├── index.html         # Web主页
│       └── ...
├── miniprogram/               # 微信小程序
│   ├── pages/                 # 小程序页面
│   │   ├── login/            # 微信一键登录
│   │   ├── user-center/      # 用户中心
│   │   ├── coins-center/     # 星币中心
│   │   ├── coins-shop/       # 星币商城
│   │   ├── star-sky/         # 星空纪念
│   │   └── ...
│   ├── config/                # 配置文件
│   │   ├── config.js         # 生产环境配置
│   │   └── config-local.js   # 本地开发配置
│   └── utils/                 # 工具函数
│       ├── api.js            # API请求封装
│       ├── wechat.js         # 微信API封装
│       └── util.js           # 通用工具
├── storage/                   # 文件存储
│   ├── photos/               # 用户照片
│   ├── memorials/            # 纪念馆数据
│   └── qrcodes/              # 二维码
├── certs/                     # SSL证书（HTTPS）
├── start_server.py           # 生产环境启动脚本
├── restart.sh                # 服务器重启脚本
├── deploy_to_server.sh       # 部署脚本
├── requirements.txt          # Python依赖
└── 文档/
    ├── README.md             # 本文档
    ├── DEPLOYMENT.md         # 部署指南
    ├── FEATURE_SUMMARY.md    # 功能详细说明
    ├── DEEPSEEK_API_SETUP.md # AI配置
    └── HTTPS配置完整指南.md  # HTTPS配置
```

---

## 🛠️ 技术栈

### 后端
- **框架**: FastAPI (Python 3.11+)
- **数据库**: SQLite
- **认证**: WeChat OAuth 2.0
- **AI**: DeepSeek API
- **模板引擎**: Jinja2

### 前端
- **小程序**: 微信小程序框架
- **Web端**: HTML5 + CSS3 + JavaScript
- **UI组件**: WeUI (小程序) / 自定义CSS (Web)

### 部署
- **服务器**: OpenCloudOS 9
- **反向代理**: (待配置 Nginx)
- **进程管理**: nohup / systemd
- **版本控制**: Git

---

## 🔧 配置说明

### 1. 环境变量配置

复制 `env_example.txt` 为 `.env`，填写以下配置：

```bash
# 微信小程序配置
WECHAT_APP_ID=你的小程序AppID
WECHAT_APP_SECRET=你的小程序AppSecret

# DeepSeek AI配置
DEEPSEEK_API_KEY=你的DeepSeek API密钥

# 数据库配置
DATABASE_PATH=./app/pet_memorials.db
```

### 2. 小程序配置

修改 `miniprogram/config/config.js`：

```javascript
const config = {
  baseUrl: 'http://pettrailstar.cn',  // 后端地址
  appId: 'wx9572f66945407446'         // 小程序AppID
};
```

---

## 📚 文档导航

- 📖 [部署指南](./DEPLOYMENT.md) - 服务器部署详细步骤
- ✨ [功能说明](./FEATURE_SUMMARY.md) - 所有功能详细介绍
- 🤖 [AI配置](./DEEPSEEK_API_SETUP.md) - DeepSeek API配置
- 🔒 [HTTPS配置](./HTTPS配置完整指南.md) - SSL证书配置指南

---

## 🌐 服务器信息

- **域名**: pettrailstar.cn
- **服务器IP**: 42.193.230.145
- **项目路径**: `/opt/pet-memory-star`
- **运行端口**: 80 (HTTP)
- **日志路径**: `/opt/pet-memory-star/app.log`

### 常用管理命令

```bash
# 查看服务状态
ps aux | grep start_server

# 查看日志
tail -f /opt/pet-memory-star/app.log

# 重启服务
bash restart.sh

# 部署更新
bash deploy_to_server.sh
```

---

## 💡 开发指南

### API接口

主要API端点：

```
POST   /api/auth/wx-login              # 微信登录
GET    /api/auth/me                    # 获取当前用户
GET    /api/memorials                  # 获取纪念馆列表
POST   /api/memorials                  # 创建纪念馆
GET    /api/coins/balance              # 获取星币余额
POST   /api/coins/sign-in              # 每日签到
POST   /api/ai-chat/send               # AI对话
GET    /api/star-sky/memorials         # 星空数据
```

详细API文档请查看 `app/main.py`

### 数据库表结构

主要数据表：

- `users` - 用户表（支持微信登录）
- `pet_memorials` - 纪念馆表
- `user_coins` - 用户星币余额
- `coin_transactions` - 星币交易记录
- `daily_sign_in` - 签到记录
- `ai_conversations` - AI对话记录

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 开源协议

本项目采用 MIT 协议开源。

---

## 💖 致谢

感谢所有为这个项目做出贡献的人，让我们一起用技术传递温暖。

**让爱永恒，让回忆温暖** ❤️

---

**版本**: v1.0.0  
**最后更新**: 2025-11-08  
**作者**: Pet Memory Star Team
