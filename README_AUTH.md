# 用户认证系统说明

## 概述

宠忆星·云纪念馆现已集成完整的用户认证系统，支持用户注册、登录、权限管理和纪念馆管理功能。

## 功能特性

### 1. 用户管理
- **用户注册**: 支持邮箱、密码注册
- **用户登录**: 支持邮箱登录
- **会话管理**: 基于Token的会话管理，有效期30天
- **用户等级**: 支持不同用户等级和权限控制

### 2. 权限系统
- **用户等级**: Free、Advanced、Professional三个等级
- **权限控制**: 
  - 最大纪念馆数量限制
  - AI功能使用权限
  - 导出功能权限
  - 自定义域名权限

### 3. 纪念馆管理
- **用户关联**: 纪念馆与用户关联
- **权限检查**: 创建纪念馆前检查用户权限
- **纪念馆管理**: 查看、编辑、删除自己的纪念馆

## 数据库结构

### 用户相关表
- `users`: 用户基本信息
- `user_sessions`: 用户会话管理
- `user_levels`: 用户等级定义
- `user_memorials`: 用户与纪念馆关联

### 纪念馆相关表
- `pets`: 宠物信息（新增user_id字段）
- `memorials`: 纪念馆信息（新增theme_template、is_public字段）

## API接口

### 认证相关
- `POST /api/auth/register`: 用户注册
- `POST /api/auth/login`: 用户登录
- `POST /api/auth/logout`: 用户登出
- `GET /api/auth/me`: 获取当前用户信息
- `GET /api/auth/can-create-memorial`: 检查是否可以创建纪念馆

### 纪念馆管理
- `DELETE /api/memorials/{memorial_id}`: 删除纪念馆

## 前端页面

### 认证页面
- `/login`: 登录页面
- `/register`: 注册页面
- `/dashboard`: 用户中心页面

### 功能集成
- 首页动态显示登录状态
- 创建纪念馆前检查登录状态
- 用户中心管理纪念馆

## 使用方法

### 1. 启动服务
```bash
python start_server.py
```

### 2. 用户注册
访问 `/register` 页面或调用注册API：
```json
POST /api/auth/register
{
    "email": "test@example.com",
    "password": "123456"
}
```

### 3. 用户登录
访问 `/login` 页面或调用登录API：
```json
POST /api/auth/login
{
    "email": "test@example.com",
    "password": "123456"
}
```

### 4. 创建纪念馆
登录后访问 `/personality-test` 页面开始创建纪念馆。

### 5. 管理纪念馆
访问 `/dashboard` 页面查看和管理自己的纪念馆。

## 测试

运行测试脚本验证系统功能：
```bash
python test_auth.py
```

## 安全特性

- 密码加盐哈希存储
- 会话Token安全生成
- 用户权限验证
- 纪念馆所有权验证

## 用户等级说明

### Free用户（默认）
- 最大纪念馆数量：1个
- 最大照片数量：10张
- AI功能：禁用
- 导出功能：禁用
- 自定义域名：禁用

### Advanced用户
- 最大纪念馆数量：5个
- 最大照片数量：50张
- AI功能：启用
- 导出功能：启用
- 自定义域名：禁用

### Professional用户
- 最大纪念馆数量：无限
- 最大照片数量：无限
- AI功能：启用
- 导出功能：启用
- 自定义域名：启用

## 注意事项

1. 首次运行时会自动创建数据库表结构
2. 用户等级信息会在首次运行时自动初始化
3. 所有API调用（除注册登录外）都需要在请求头中包含认证Token
4. 纪念馆创建现在需要用户登录
5. 用户只能管理自己的纪念馆
