# 代码优化计划 🔧

> 让代码更优雅、更健壮、更易维护

---

## 📊 优化概览

### 已完成 ✅
- [x] 统一API响应格式 (`utils/response.py`)
- [x] 统一日志系统 (`utils/logger.py`)
- [x] 自定义异常类 (`utils/exceptions.py`)
- [x] 全局异常处理中间件 (`middlewares/exception_handler.py`)

### 进行中 🚧
- [ ] 优化CoinsService使用新的异常系统
- [ ] 优化前端API请求错误处理
- [ ] 添加加载状态和骨架屏

### 待开始 📝
- [ ] 数据库连接池优化
- [ ] 图片压缩和懒加载
- [ ] 请求频率限制
- [ ] 参数验证增强

---

## 🎯 优化详情

### 1. 统一API响应格式 ⭐⭐⭐⭐⭐

#### 问题
- 不同API返回格式不统一
- 前端需要处理各种响应格式
- 错误信息不规范

#### 解决方案
创建 `utils/response.py`：

```python
# 成功响应
ApiResponse.success(data={...}, message="操作成功")

# 错误响应
ApiResponse.error(message="操作失败", code=4001)

# 分页响应
ApiResponse.paginated(data=[...], total=100, page=1)
```

#### 标准响应格式
```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": {...},
  "timestamp": "2025-11-08T14:30:00"
}
```

#### 错误码规范
```
1xxx - 通用错误
2xxx - 认证错误
3xxx - 用户错误
4xxx - 业务错误
5xxx - 系统错误
```

---

### 2. 统一日志系统 ⭐⭐⭐⭐⭐

#### 问题
- 日志格式不统一
- 缺少日志轮转
- 错误日志没有单独记录

#### 解决方案
创建 `utils/logger.py`：

```python
from utils.logger import log_info, log_error, log_warning

# 记录信息
log_info("用户登录", user_id=123)

# 记录错误
log_error("数据库操作失败", error=e, user_id=123)

# 记录API请求
log_api_request("POST", "/api/coins/sign-in", user_id=123)
```

#### 日志文件
```
logs/
├── app.log          # 所有日志
├── app_error.log    # 错误日志
└── ...
```

#### 日志格式
```
2025-11-08 14:30:00 | INFO     | app | 用户登录 {'user_id': 123}
2025-11-08 14:30:01 | ERROR    | app | 数据库操作失败 ...
```

---

### 3. 自定义异常类 ⭐⭐⭐⭐⭐

#### 问题
- 使用通用Exception，不够语义化
- 错误处理逻辑分散
- 难以区分不同类型的错误

#### 解决方案
创建 `utils/exceptions.py`：

```python
# 业务异常
raise BusinessException("操作失败", code=400)

# 认证异常
raise AuthException("登录已过期")

# 星币不足
raise InsufficientCoinsException("星币余额不足")

# 资源不存在
raise NotFoundException("纪念馆不存在")
```

#### 异常层次
```
BusinessException (基类)
├── AuthException (认证异常)
├── PermissionException (权限异常)
├── NotFoundException (资源不存在)
├── ValidationException (参数验证)
├── InsufficientCoinsException (星币不足)
└── DatabaseException (数据库异常)
```

---

### 4. 全局异常处理中间件 ⭐⭐⭐⭐⭐

#### 问题
- 每个API都要写try-catch
- 异常处理逻辑重复
- 未捕获的异常导致500错误

#### 解决方案
创建 `middlewares/exception_handler.py`：

```python
# 自动捕获所有异常
# 自动记录请求日志
# 自动记录响应时间
# 统一返回错误格式
```

#### 使用方式
```python
# main.py
from middlewares.exception_handler import ExceptionHandlerMiddleware

app.add_middleware(ExceptionHandlerMiddleware)
```

#### 效果
```python
# 之前
@app.post("/api/coins/sign-in")
async def sign_in(user: dict = Depends(get_current_user)):
    try:
        result = coins_service.daily_sign_in(user['id'])
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "message": str(e)}

# 之后
@app.post("/api/coins/sign-in")
async def sign_in(user: dict = Depends(get_current_user)):
    success, result, reward = coins_service.daily_sign_in(user['id'])
    if not success:
        raise BusinessException(result)
    return ApiResponse.success(data=result, message="签到成功")
```

---

## 🚀 下一步优化

### 5. 优化CoinsService

#### 目标
- 使用新的异常系统
- 添加详细日志
- 优化返回值格式
- 添加类型注解

#### 示例
```python
def daily_sign_in(self, user_id: int) -> Dict:
    """
    每日签到
    :param user_id: 用户ID
    :return: 签到结果
    :raises BusinessException: 今日已签到
    """
    log_info(f"用户签到", user_id=user_id)
    
    cursor = self.db.conn.cursor()
    today = date.today().isoformat()
    
    # 检查今天是否已签到
    cursor.execute('''
        SELECT id FROM daily_sign_in 
        WHERE user_id = ? AND sign_date = ?
    ''', (user_id, today))
    
    if cursor.fetchone():
        raise BusinessException("今日已签到", code=4002)
    
    # ... 签到逻辑
    
    log_info(f"签到成功", user_id=user_id, reward=reward)
    return {
        'reward': reward,
        'continuous_days': continuous_days,
        'message': f'签到成功！连续签到{continuous_days}天'
    }
```

---

### 6. 前端错误处理优化

#### 目标
- 统一错误提示
- 根据错误码显示不同提示
- 自动处理token过期

#### 示例
```javascript
// utils/api.js
function handleError(error) {
  const { code, message } = error;
  
  switch(code) {
    case 2001: // 未登录
    case 2002: // token过期
      wx.showModal({
        title: '登录已过期',
        content: '请重新登录',
        success: (res) => {
          if (res.confirm) {
            wx.navigateTo({ url: '/pages/login/login' });
          }
        }
      });
      break;
    
    case 4001: // 星币不足
      wx.showModal({
        title: '星币不足',
        content: message,
        confirmText: '去赚星币',
        success: (res) => {
          if (res.confirm) {
            wx.navigateTo({ url: '/pages/coins-center/coins-center' });
          }
        }
      });
      break;
    
    default:
      wx.showToast({
        title: message || '操作失败',
        icon: 'none'
      });
  }
}
```

---

### 7. 加载状态优化

#### 目标
- 添加全局loading
- 添加骨架屏
- 防止重复请求

#### 示例
```javascript
// 全局loading
wx.showLoading({ title: '加载中...' });
try {
  const res = await api.request('/api/coins/balance');
  // 处理数据
} finally {
  wx.hideLoading();
}

// 骨架屏
<view class="skeleton" wx:if="{{loading}}">
  <view class="skeleton-avatar"></view>
  <view class="skeleton-text"></view>
  <view class="skeleton-text"></view>
</view>

<view class="content" wx:else>
  <!-- 真实内容 -->
</view>
```

---

### 8. 数据库优化

#### 目标
- 添加连接池
- 优化事务管理
- 添加索引

#### 示例
```python
# 添加索引
CREATE INDEX idx_user_coins_user_id ON user_coins(user_id);
CREATE INDEX idx_coin_transactions_user_id ON coin_transactions(user_id);
CREATE INDEX idx_daily_sign_in_user_date ON daily_sign_in(user_id, sign_date);

# 事务管理
with self.db.transaction():
    # 扣除星币
    self.spend_coins(user_id, amount)
    # 增加会员时长
    self.add_membership(user_id, days)
```

---

### 9. 图片优化

#### 目标
- 上传时自动压缩
- 生成缩略图
- 懒加载

#### 示例
```python
from PIL import Image

def compress_image(image_path, quality=85):
    """压缩图片"""
    img = Image.open(image_path)
    
    # 限制最大尺寸
    max_size = (1920, 1920)
    img.thumbnail(max_size, Image.LANCZOS)
    
    # 保存压缩后的图片
    img.save(image_path, quality=quality, optimize=True)
    
    # 生成缩略图
    thumbnail_path = image_path.replace('.jpg', '_thumb.jpg')
    img.thumbnail((400, 400), Image.LANCZOS)
    img.save(thumbnail_path, quality=80)
```

---

### 10. 安全优化

#### 目标
- 请求频率限制
- 参数验证
- SQL注入防护

#### 示例
```python
from fastapi import Depends
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/coins/sign-in")
@limiter.limit("10/minute")  # 每分钟最多10次
async def sign_in(user: dict = Depends(get_current_user)):
    # ... 签到逻辑
    pass
```

---

## 📈 优化效果预期

### 代码质量
- ✅ 代码更易读
- ✅ 错误处理更规范
- ✅ 日志更完善
- ✅ 更易维护

### 用户体验
- ✅ 错误提示更友好
- ✅ 加载状态更清晰
- ✅ 响应速度更快
- ✅ 更少的bug

### 开发效率
- ✅ 减少重复代码
- ✅ 更快定位问题
- ✅ 更容易扩展
- ✅ 更好的协作

---

## 🎯 优化时间表

| 阶段 | 内容 | 预计时间 | 优先级 |
|------|------|----------|--------|
| Phase 1 | 基础架构优化 | 2小时 | ⭐⭐⭐⭐⭐ |
| Phase 2 | 服务层优化 | 3小时 | ⭐⭐⭐⭐ |
| Phase 3 | 前端优化 | 3小时 | ⭐⭐⭐⭐ |
| Phase 4 | 性能优化 | 2小时 | ⭐⭐⭐ |
| Phase 5 | 安全加固 | 2小时 | ⭐⭐⭐⭐ |

**总计**: 12小时

---

## 📝 优化检查清单

### 后端
- [x] 统一API响应格式
- [x] 统一日志系统
- [x] 全局异常处理
- [ ] 优化所有Service类
- [ ] 添加参数验证
- [ ] 添加请求限流
- [ ] 数据库索引优化
- [ ] 图片处理优化

### 前端
- [ ] 统一错误处理
- [ ] 添加loading状态
- [ ] 添加骨架屏
- [ ] 图片懒加载
- [ ] 防抖节流
- [ ] 请求去重
- [ ] 缓存优化

### 文档
- [ ] API文档完善
- [ ] 代码注释完善
- [ ] 部署文档更新
- [ ] 优化文档归档

---

**让代码更优雅，让系统更健壮！** 💪

