# 爪迹星·小程序端 📱

> 微信小程序版 - 随时随地怀念你的毛孩子

---

## 🚀 快速开始

### 1. 打开项目

使用微信开发者工具打开本目录（`miniprogram`）

### 2. 配置AppID

在 `project.config.json` 中配置你的小程序AppID：

```json
{
  "appid": "wx9572f66945407446"
}
```

### 3. 配置后端地址

修改 `config/config.js`：

```javascript
const config = {
  baseUrl: 'http://pettrailstar.cn',  // 生产环境
  appId: 'wx9572f66945407446'
};
```

本地开发时使用 `config/config-local.js`：

```javascript
const config = {
  baseUrl: 'http://localhost:80',  // 本地环境
  appId: 'wx9572f66945407446'
};
```

### 4. 编译运行

点击微信开发者工具的"编译"按钮即可预览

---

## 📁 目录结构

```
miniprogram/
├── pages/                    # 页面目录
│   ├── index/               # 首页
│   ├── login/               # 微信一键登录
│   ├── user-center/         # 用户中心
│   ├── memorials/           # 纪念馆列表
│   ├── memorial-detail/     # 纪念馆详情
│   ├── memorial-edit/       # 创建/编辑纪念馆
│   ├── star-sky/            # 星空纪念
│   ├── coins-center/        # 星币中心
│   ├── coins-shop/          # 星币商城
│   ├── ai-chat/             # AI对话
│   ├── personality-test/    # 性格测试
│   ├── mood-diary/          # 心情日记
│   ├── dream-diary/         # 梦境日记
│   ├── virtual-companion/   # 虚拟陪伴
│   ├── photo-manager/       # 照片管理
│   ├── reminder-setup/      # 提醒设置
│   ├── theme-settings/      # 主题设置
│   ├── payment/             # 支付页面
│   └── orders/              # 订单页面
├── config/                   # 配置文件
│   ├── config.js            # 生产环境配置
│   └── config-local.js      # 本地开发配置
├── utils/                    # 工具函数
│   ├── api.js               # API请求封装
│   ├── wechat.js            # 微信API封装
│   ├── util.js              # 通用工具函数
│   └── network.js           # 网络请求工具
├── app.js                    # 小程序入口
├── app.json                  # 全局配置
├── app.wxss                  # 全局样式
├── project.config.json       # 项目配置
└── sitemap.json             # 索引配置
```

---

## 🎨 主要页面

### 登录流程
1. **login** - 微信一键登录（获取openid）
2. 自动跳转到用户中心

### 核心功能页面
- **index** - 首页（纪念馆展示）
- **memorials** - 我的纪念馆列表
- **memorial-detail** - 纪念馆详情页
- **memorial-edit** - 创建/编辑纪念馆
- **star-sky** - 3D星空展示

### 互动功能
- **ai-chat** - AI对话陪伴
- **personality-test** - 宠物性格测试
- **mood-diary** - 心情日记本
- **dream-diary** - 梦境记录
- **virtual-companion** - 虚拟陪伴互动

### 星币系统
- **coins-center** - 星币中心（签到、任务）
- **coins-shop** - 星币商城（兑换会员）
- **user-center** - 用户中心（余额显示）

---

## 🔌 API调用

### 使用示例

```javascript
// 在页面中导入app实例
const app = getApp();

// 调用API
async function getData() {
  try {
    const res = await app.request('/api/memorials', 'GET');
    console.log('获取成功:', res);
  } catch (error) {
    console.error('请求失败:', error);
  }
}
```

### API方法

`app.request(url, method, data, options)`

- `url`: API路径（自动拼接baseUrl）
- `method`: 请求方法（GET/POST/PUT/DELETE）
- `data`: 请求数据
- `options`: 额外配置（如 `noAuth: true` 跳过认证）

---

## 🎯 功能特性

### ✅ 微信登录
- 使用 `wx.login()` 获取code
- 后端换取openid和session_key
- 自动管理session_token

### ✅ 星币系统
- 每日签到奖励（连续签到加倍）
- 任务完成奖励
- 星币兑换会员

### ✅ AI对话
- 接入DeepSeek AI
- 支持多轮对话
- 情感化回复

### ✅ 3D星空
- Three.js渲染
- 交互式点击
- 粒子动画效果

### ✅ 照片管理
- 多图上传
- 照片轮播
- 删除编辑

---

## 🔧 常见问题

### 1. 登录失败？

**检查项**：
- AppID和AppSecret是否正确配置
- 后端服务是否正常运行
- 网络请求域名是否配置白名单

**解决方案**：
在微信公众平台 → 开发 → 开发管理 → 服务器域名，添加：
```
request合法域名: http://pettrailstar.cn
```

### 2. API请求失败？

**检查项**：
- 检查 `config/config.js` 中的 `baseUrl` 是否正确
- 查看控制台网络请求日志
- 确认后端服务是否正常

**调试方法**：
```javascript
// 在页面的onLoad中添加
console.log('当前配置:', getApp().globalData.config);
console.log('baseUrl:', getApp().globalData.config.baseUrl);
```

### 3. 图片上传失败？

**检查项**：
- 检查 `uploadFile` 域名白名单
- 确认图片大小（建议<2MB）
- 检查后端存储路径权限

### 4. 本地开发配置

使用本地后端开发时：

1. 修改 `app.js` 中的配置引入：
```javascript
const config = require('./config/config-local.js');
```

2. 微信开发者工具：设置 → 项目设置 → 勾选"不校验合法域名"

---

## 📱 小程序配置

### 必需配置项

在微信公众平台配置：

**1. 服务器域名**
```
request: http://pettrailstar.cn
uploadFile: http://pettrailstar.cn
downloadFile: http://pettrailstar.cn
```

**2. 业务域名**
```
http://pettrailstar.cn
```

**3. 用户隐私保护**
- 添加隐私政策链接
- 说明数据使用方式

---

## 🚢 发布流程

### 1. 准备发布

```bash
# 确保使用生产环境配置
# 修改 app.js 引入
const config = require('./config/config.js');

# 检查版本号
# 修改 app.js 中的 version
```

### 2. 上传代码

1. 微信开发者工具 → 上传
2. 填写版本号和备注
3. 提交审核

### 3. 审核发布

1. 登录微信公众平台
2. 版本管理 → 开发版本 → 提交审核
3. 审核通过后 → 发布

---

## 📊 性能优化

### 已实现的优化

- ✅ 图片懒加载
- ✅ 分页加载数据
- ✅ 请求去重和缓存
- ✅ 防抖节流处理
- ✅ 骨架屏占位

### 建议优化

- [ ] 使用CDN加速静态资源
- [ ] 启用分包加载
- [ ] 图片压缩和webp格式
- [ ] 使用小程序云开发

---

## 🎨 UI规范

### 颜色主题

```css
/* 主色调 */
--primary-color: #8B7355;      /* 温暖棕色 */
--secondary-color: #D4A574;    /* 浅金色 */
--accent-color: #FFD700;       /* 星币金色 */

/* 功能色 */
--success-color: #52c41a;      /* 成功绿 */
--warning-color: #faad14;      /* 警告黄 */
--error-color: #f5222d;        /* 错误红 */
--info-color: #1890ff;         /* 信息蓝 */

/* 中性色 */
--text-primary: #333333;       /* 主文字 */
--text-secondary: #666666;     /* 次要文字 */
--text-disabled: #999999;      /* 禁用文字 */
--border-color: #e8e8e8;       /* 边框色 */
--bg-color: #f5f5f5;           /* 背景色 */
```

### 字体规范

```css
/* 标题 */
font-size: 32rpx; font-weight: bold;

/* 正文 */
font-size: 28rpx; line-height: 1.6;

/* 辅助文字 */
font-size: 24rpx; color: #999;

/* 小字 */
font-size: 20rpx;
```

---

## 📝 更新日志

### v1.0.0 (2025-11-08)
- ✅ 微信一键登录
- ✅ 星币系统（签到、任务）
- ✅ AI对话功能
- ✅ 3D星空纪念
- ✅ 纪念馆CRUD
- ✅ 用户中心优化

---

## 💬 联系方式

如有问题或建议，请联系：

- 📧 Email: support@pettrailstar.cn
- 💬 微信: 扫描小程序码

---

**让爱永恒，让回忆温暖** ❤️
