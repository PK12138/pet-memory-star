# 🔧 创建纪念馆API修复

## 🎯 问题诊断

### 问题现象
小程序性格测试完成后，点击"创建纪念馆"按钮，显示 `404 (Not Found)` 错误。

### 错误信息
```
POST http://42.193.230.145/api/memorial/create 404 (Not Found)
API请求失败: Error: 请求失败: 404
创建纪念馆失败: Error: 请求失败: 404
```

### 根本原因

1. **API端点不存在**：
   - 小程序调用：`POST /api/memorial/create` ❌ 不存在
   - 后端只有：`POST /create-memorial-advanced` ✅ 存在

2. **数据格式不匹配**：
   - 后端 `/create-memorial-advanced` 需要 `FormData` 格式（包含文件上传）
   - 小程序发送的是 `JSON` 格式数据

3. **功能设计差异**：
   - 网页版：一次性上传所有数据（宠物信息+照片）
   - 小程序：分步操作（先创建纪念馆，后上传照片）

---

## 🔧 修复方案

### 1. 新增小程序专用API

在 `app/main.py` 中添加 `POST /api/memorial/create` 端点：

```python
@app.post("/api/memorial/create")
async def create_memorial_json(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """创建纪念馆API（JSON格式，适用于小程序）"""
    try:
        data = await request.json()
        
        # 获取用户信息
        user_id = current_user["id"]
        user_email = current_user["email"]
        
        # 检查用户权限
        permission_check = auth_service.can_create_memorial(user_id)
        if not permission_check["can_create"]:
            return JSONResponse(
                content={
                    "success": False,
                    "message": permission_check["message"]
                },
                status_code=403
            )
        
        # 获取提交的数据
        pet_name = data.get("pet_name", "")
        breed = data.get("breed", "")
        species = breed  # 使用breed作为species
        age = data.get("age", "")
        gender = data.get("gender", "")
        description = data.get("description", "")
        personality = data.get("personality", "")
        
        # 构建宠物信息
        import datetime
        pet_info = {
            "name": pet_name,
            "species": species,
            "breed": breed,
            "gender": gender,
            "birth_date": "",
            "memorial_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "weight": 0.0,
            "status": "alive"
        }
        
        # 创建纪念馆（暂时不上传照片）
        memorial_url, personality_type, ai_letter = memorial_service.create_memorial_advanced(
            email=user_email,
            pet_info=pet_info,
            photos=[],  # 小程序可以稍后上传照片
            personality_answers={},
            user_id=user_id
        )
        
        # 返回成功结果
        return JSONResponse(
            content={
                "success": True,
                "message": "纪念馆创建成功",
                "memorial_url": memorial_url,
                "memorial_id": memorial_url.split("/")[-1] if memorial_url else "",
                "personality_type": personality_type,
                "ai_letter": ai_letter
            }
        )
    
    except Exception as e:
        print(f"❌ 创建纪念馆失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            content={
                "success": False,
                "message": f"创建失败：{str(e)}"
            },
            status_code=500
        )
```

---

## ✅ 修复内容

### 1. 新增API端点
- **路径**：`POST /api/memorial/create`
- **格式**：接受JSON数据
- **认证**：需要Bearer Token
- **适用**：小程序

### 2. 请求参数

```json
{
  "pet_name": "宠物名称",
  "breed": "宠物品种",
  "age": "宠物年龄",
  "gender": "性别（公/母）",
  "description": "纪念馆描述",
  "personality": "性格分析结果"
}
```

### 3. 响应格式

**成功**：
```json
{
  "success": true,
  "message": "纪念馆创建成功",
  "memorial_url": "/memorial/abc123",
  "memorial_id": "abc123",
  "personality_type": "活泼好动",
  "ai_letter": "AI生成的信件内容"
}
```

**失败**：
```json
{
  "success": false,
  "message": "错误信息"
}
```

### 4. 权限检查
- ✅ 检查用户是否有创建纪念馆的权限
- ✅ 基于用户等级限制

---

## 🚀 部署步骤

### 1. 重启服务器

如果后端在服务器上运行，需要重启：

```bash
# SSH登录服务器
ssh root@42.193.230.145

# 找到运行的进程
ps aux | grep uvicorn

# 杀掉进程
kill -9 <进程ID>

# 重新启动
cd /opt/pet-memory-star
source venv/bin/activate
nohup python start_server.py > server.log 2>&1 &
```

### 2. 本地测试

如果在本地测试：

```bash
# 停止当前服务器（Ctrl+C）

# 重新启动
cd D:\code\pet-memory-star
venv\Scripts\python.exe start_local.py
```

### 3. 验证API

测试新API是否可用：

```bash
# 使用curl测试（需要先登录获取token）
curl -X POST http://42.193.230.145/api/memorial/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
  -d '{
    "pet_name": "测试宠物",
    "breed": "测试品种",
    "age": "3",
    "gender": "公",
    "description": "测试描述",
    "personality": "活泼好动"
  }'
```

---

## 📊 API对比

| 特性 | 网页版API | 小程序API |
|-----|----------|----------|
| **端点** | `/create-memorial-advanced` | `/api/memorial/create` |
| **方法** | POST | POST |
| **格式** | FormData (multipart/form-data) | JSON (application/json) |
| **认证** | Bearer Token | Bearer Token |
| **照片** | 必须上传 | 可选（稍后上传） |
| **必填字段** | email, pet_name, species, memorial_date, photos | pet_name, breed |
| **返回** | HTML or JSON | JSON |
| **适用** | 网页表单提交 | 小程序API调用 |

---

## 🧪 测试步骤

### 1. 重新编译小程序
确保使用最新代码。

### 2. 完成性格测试
1. 填写宠物信息
2. 回答10道题目
3. 查看性格分析结果

### 3. 创建纪念馆
1. 填写纪念馆描述
2. 点击"创建纪念馆"按钮
3. **检查Console**：
   - 应该看到 `POST /api/memorial/create` 请求
   - 状态码应该是 200（而不是404）
   - 响应中 `success: true`

### 4. 预期结果
```
请求成功：
POST http://42.193.230.145/api/memorial/create 200 OK

响应内容：
{
  "success": true,
  "message": "纪念馆创建成功",
  "memorial_id": "xxx",
  ...
}

跳转到纪念馆列表
```

---

## ⚠️ 注意事项

### 1. 服务器必须重启
新API只有在重启服务器后才会生效。

### 2. 小程序代码不需要修改
小程序的 `personality-test.js` 已经正确调用 `/api/memorial/create`，不需要改动。

### 3. 照片上传
创建纪念馆时暂不上传照片，用户可以：
- 在纪念馆列表中进入已创建的纪念馆
- 使用"编辑纪念馆"功能上传照片
- 或使用"照片管理"功能上传

### 4. 性格测试答案
当前版本创建纪念馆时：
- 性格分析结果：从小程序传入的 `personality` 字段
- 性格测试答案：未保存（传空对象`{}`）
- 如需保存测试答案，需要在小程序中收集答案并一起提交

---

## 🔍 故障排查

### 问题1：仍然显示404

**检查**：
- 服务器是否已重启
- 新代码是否已部署到服务器
- API路径是否正确

**解决**：
```bash
# 确认文件已更新
cat /opt/pet-memory-star/app/main.py | grep "api/memorial/create"

# 应该看到新添加的 @app.post("/api/memorial/create")
```

### 问题2：权限不足

**检查**：
- 用户是否已登录
- sessionToken是否有效
- 用户等级是否允许创建纪念馆

**解决**：
- 重新登录
- 检查用户等级设置
- 查看数据库user_levels表

### 问题3：创建成功但数据库没有记录

**检查**：
- 数据库文件路径
- `memorial_service.create_memorial_advanced()` 是否正常执行

**解决**：
- 查看服务器日志
- 检查数据库文件权限

---

## 📝 后续优化

### 1. 保存性格测试答案

修改小程序 `personality-test.js`：

```javascript
async createMemorial() {
  const { petInfo, memorialInfo, personalityResult, answers } = this.data
  
  // ... 现有代码 ...
  
  const res = await app.request({
    url: '/api/memorial/create',
    method: 'POST',
    data: {
      pet_name: petInfo.name,
      breed: petInfo.breed,
      age: petInfo.age,
      gender: petInfo.gender,
      description: memorialInfo.description,
      personality: personalityResult,
      personality_answers: answers  // 添加测试答案
    }
  })
}
```

修改后端API：

```python
# 在 create_memorial_json 函数中
personality_answers = data.get("personality_answers", {})

# 创建纪念馆时传入
memorial_url, personality_type, ai_letter = memorial_service.create_memorial_advanced(
    email=user_email,
    pet_info=pet_info,
    photos=[],
    personality_answers=personality_answers,  # 传入答案
    user_id=user_id
)
```

### 2. 支持照片上传

可以分两步：
1. 第一步：创建纪念馆（不带照片）
2. 第二步：使用 `POST /api/memorial/upload-photos/:memorial_id` 上传照片

### 3. 完善数据验证

添加更多字段验证：
- pet_name 不能为空
- description 长度限制
- age 必须是数字

---

**✨ 修复完成！重启服务器后，小程序应该可以成功创建纪念馆了。**

_修复时间: 2025-01-14_


