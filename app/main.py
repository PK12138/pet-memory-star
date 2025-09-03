from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException, Depends, Header
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database import Database
from services import MemorialService, EmailService
from auth_service import AuthService
import os
import uuid
import uvicorn
import json
from typing import Optional

app = FastAPI(title="宠忆星·云纪念馆")

# 挂载静态文件目录
# 当从项目根目录运行时，storage目录在项目根目录下
storage_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage")
print(f"📁 静态文件目录: {storage_path}")
if os.path.exists(storage_path):
    app.mount("/storage", StaticFiles(directory=storage_path), name="storage")
    print(f"✅ 静态文件服务已挂载到 /storage")
else:
    print(f"❌ 静态文件目录不存在: {storage_path}")

# 初始化模板
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

# 初始化服务
db = Database()
memorial_service = MemorialService(db)
email_service = EmailService()
auth_service = AuthService(db)

# 依赖函数：获取当前用户
async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供有效的认证令牌")
    
    session_token = authorization.replace("Bearer ", "")
    user = auth_service.get_current_user(session_token)
    
    if not user:
        raise HTTPException(status_code=401, detail="认证令牌无效或已过期")
    
    return user

@app.get("/", response_class=HTMLResponse)
async def index():
    """首页"""
    try:
        # 使用绝对路径读取模板文件
        template_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        return HTMLResponse(content=f"<h1>页面加载错误</h1><p>{str(e)}</p>", status_code=500)

@app.get("/login", response_class=HTMLResponse)
async def login_page():
    """登录页面"""
    try:
        template_path = os.path.join(os.path.dirname(__file__), "templates", "login.html")
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        return HTMLResponse(content=f"<h1>页面加载错误</h1><p>{str(e)}</p>", status_code=500)

@app.get("/register", response_class=HTMLResponse)
async def register_page():
    """注册页面"""
    try:
        template_path = os.path.join(os.path.dirname(__file__), "templates", "register.html")
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        return HTMLResponse(content=f"<h1>页面加载错误</h1><p>{str(e)}</p>", status_code=500)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page():
    """用户中心页面"""
    try:
        template_path = os.path.join(os.path.dirname(__file__), "templates", "dashboard.html")
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        return HTMLResponse(content=f"<h1>页面加载错误</h1><p>{str(e)}</p>", status_code=500)

@app.get("/personality-test", response_class=HTMLResponse)
async def personality_test_page():
    """性格测试页面"""
    try:
        template_path = os.path.join(os.path.dirname(__file__), "templates", "personality_test.html")
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        return HTMLResponse(content=f"<h1>页面加载错误</h1><p>{str(e)}</p>", status_code=500)

@app.get("/theme-selector", response_class=HTMLResponse)
async def theme_selector_page():
    """主题选择页面"""
    try:
        template_path = os.path.join(os.path.dirname(__file__), "templates", "theme_selector.html")
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        return HTMLResponse(content=f"<h1>页面加载错误</h1><p>{str(e)}</p>", status_code=500)

@app.get("/reminder-setup", response_class=HTMLResponse)
async def reminder_setup_page():
    """纪念日提醒设置页面"""
    try:
        template_path = os.path.join(os.path.dirname(__file__), "templates", "reminder_setup.html")
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        return HTMLResponse(content=f"<h1>页面加载错误</h1><p>{str(e)}</p>", status_code=500)

# 认证相关API
@app.post("/api/auth/register")
async def register_user(request: Request):
    """用户注册API"""
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")
        
        result = auth_service.register_user(email, password)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(
            content={"success": False, "message": f"注册失败：{str(e)}"},
            status_code=500
        )

@app.post("/api/auth/login")
async def login_user(request: Request):
    """用户登录API"""
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")
        
        # 获取客户端IP和User-Agent
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        result = auth_service.login_user(email, password, client_ip, user_agent)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(
            content={"success": False, "message": f"登录失败：{str(e)}"},
            status_code=500
        )

@app.post("/api/auth/logout")
async def logout_user(request: Request, current_user: dict = Depends(get_current_user)):
    """用户登出API"""
    try:
        # 从请求头获取session_token
        authorization = request.headers.get("authorization")
        if authorization and authorization.startswith("Bearer "):
            session_token = authorization.replace("Bearer ", "")
            result = auth_service.logout_user(session_token)
            return JSONResponse(content=result)
        else:
            return JSONResponse(content={"success": True, "message": "登出成功"})
    except Exception as e:
        return JSONResponse(
            content={"success": False, "message": f"登出失败：{str(e)}"},
            status_code=500
        )

@app.get("/api/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """获取当前用户信息API"""
    try:
        # 获取用户仪表板数据
        dashboard_data = auth_service.get_user_dashboard_data(current_user["id"])
        
        return JSONResponse(content={
            "success": True,
            "user": current_user,
            "dashboard_data": dashboard_data
        })
    except Exception as e:
        return JSONResponse(
            content={"success": False, "message": f"获取用户信息失败：{str(e)}"},
            status_code=500
        )

@app.get("/api/auth/can-create-memorial")
async def check_can_create_memorial(current_user: dict = Depends(get_current_user)):
    """检查用户是否可以创建纪念馆"""
    try:
        result = auth_service.can_create_memorial(current_user["id"])
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(
            content={"can_create": False, "message": f"检查失败：{str(e)}"},
            status_code=500
        )

@app.delete("/api/memorials/{memorial_id}")
async def delete_memorial(memorial_id: str, current_user: dict = Depends(get_current_user)):
    """删除纪念馆"""
    try:
        # 检查纪念馆是否属于当前用户
        user_memorials = db.get_user_memorials(current_user["id"])
        memorial_belongs_to_user = any(memorial[0] == memorial_id for memorial in user_memorials)
        
        if not memorial_belongs_to_user:
            return JSONResponse(
                content={"success": False, "message": "无权删除此纪念馆"},
                status_code=403
            )
        
        # 删除纪念馆文件
        storage_base = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage")
        memorial_path = os.path.join(storage_base, "memorials", f"{memorial_id}.html")
        if os.path.exists(memorial_path):
            os.remove(memorial_path)
        
        # 从数据库中删除纪念馆记录
        if db.delete_memorial(memorial_id, current_user["id"]):
            return JSONResponse(content={"success": True, "message": "纪念馆删除成功"})
        else:
            return JSONResponse(
                content={"success": False, "message": "删除失败：纪念馆不存在或无权限"},
                status_code=404
            )
    except Exception as e:
        return JSONResponse(
            content={"success": False, "message": f"删除失败：{str(e)}"},
            status_code=500
        )

@app.get("/api/personality-questions")
async def get_personality_questions():
    """获取性格测试问题"""
    questions = memorial_service.get_personality_questions()
    return {"questions": questions}

@app.get("/api/personality-options/{question_id}")
async def get_personality_options(question_id: int):
    """获取指定问题的答案选项"""
    options = memorial_service.get_personality_answer_options(question_id)
    return {"options": options}

@app.post("/create-memorial-advanced")
async def create_memorial_advanced(
    request: Request,
    current_user: dict = Depends(get_current_user),  # 要求用户登录
    email: str = Form(...),
    pet_name: str = Form(...),
    species: str = Form(...),
    breed: str = Form(""),
    color: str = Form(""),
    gender: str = Form(""),
    birth_date: str = Form(""),
    memorial_date: str = Form(...),
    weight: float = Form(0.0),
    pet_status: str = Form("alive"),
    photos: list[UploadFile] = File(...),
    personality_answers: str = Form("{}")
):
    """创建纪念馆完整流程（包含性格测试和AI信件）"""
    try:
        # 解析性格测试答案
        try:
            personality_answers_dict = json.loads(personality_answers)
        except:
            personality_answers_dict = {}
        
        # 保存上传的图片
        photo_paths = []
        for photo in photos:
            filename = f"{uuid.uuid4().hex}.jpg"
            # 使用绝对路径保存照片
            storage_base = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage")
            path = os.path.join(storage_base, "photos", filename)
            with open(path, "wb") as f:
                f.write(await photo.read())
            photo_paths.append(f"/storage/photos/{filename}")
        
        # 构建宠物信息
        pet_info = {
            "name": pet_name,
            "species": species,
            "breed": breed,
            "color": color,
            "gender": gender,
            "birth_date": birth_date,
            "memorial_date": memorial_date,
            "weight": weight,
            "status": pet_status
        }
        
        # 创建纪念馆
        memorial_url, personality_type, ai_letter = memorial_service.create_memorial_advanced(
            email=email,
            pet_info=pet_info,
            photos=photo_paths,
            personality_answers=personality_answers_dict,
            user_id=current_user["id"]  # 传递当前用户ID
        )
        
        # 发送通知邮件
        email_service.send_creation_email(
            email=email, 
            pet_name=pet_name, 
            memorial_url=memorial_url,
            personality_type=personality_type,
            ai_letter=ai_letter
        )
        
        return {
            "success": True, 
            "memorial_url": memorial_url,
            "personality_type": personality_type,
            "ai_letter": ai_letter
        }
    
    except Exception as e:
        return {"success": False, "error": str(e)}



@app.get("/memorial/{memorial_id}", response_class=HTMLResponse)
def view_memorial(memorial_id: str):
    """查看纪念馆页面"""
    # 使用绝对路径读取纪念馆文件
    storage_base = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage")
    memorial_path = os.path.join(storage_base, "memorials", f"{memorial_id}.html")
    if not os.path.exists(memorial_path):
        return HTMLResponse(content="<h1>纪念馆不存在</h1>", status_code=404)
    
    with open(memorial_path, "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content=content)

@app.get("/api/test-email")
async def test_email(email: str):
    """测试邮件发送功能"""
    try:
        success = email_service.send_test_email(email)
        if success:
            return {"success": True, "message": "测试邮件发送成功，请检查邮箱"}
        else:
            return {"success": False, "message": "测试邮件发送失败，请检查邮件配置"}
    except Exception as e:
        return {"success": False, "message": f"邮件测试异常: {str(e)}"}

@app.get("/api/email-config")
async def get_email_config():
    """获取邮件配置信息"""
    import os
    return {
        "smtp_server": os.getenv('SMTP_SERVER', 'smtp.163.com'),
        "smtp_port": os.getenv('SMTP_PORT', '587'),
        "sender_email": os.getenv('SENDER_EMAIL', 'your_email@163.com'),
        "has_password": bool(os.getenv('SENDER_PASSWORD'))
    }

# 密码找回相关API
@app.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page():
    """忘记密码页面"""
    try:
        template_path = os.path.join(os.path.dirname(__file__), "templates", "forgot_password.html")
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        return HTMLResponse(content=f"<h1>页面加载错误</h1><p>{str(e)}</p>", status_code=500)

@app.post("/api/auth/send-verification-code")
async def send_verification_code(request: Request):
    """发送邮箱验证码"""
    try:
        data = await request.json()
        email = data.get('email', '').strip()
        
        if not email:
            return {"success": False, "message": "请输入邮箱地址"}
        
        # 检查邮箱格式
        import re
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            return {"success": False, "message": "邮箱格式不正确"}
        
        # 检查用户是否存在
        if not db.user_exists(email):
            return {"success": False, "message": "该邮箱未注册，请先注册账户"}
        
        # 生成验证码
        code = db.create_email_code(email, "password_reset")
        
        # 发送验证码邮件
        success = email_service.send_verification_code(email, code)
        
        if success:
            return {"success": True, "message": "验证码已发送到您的邮箱"}
        else:
            return {"success": False, "message": "验证码发送失败，请稍后重试"}
            
    except Exception as e:
        print(f"发送验证码失败: {e}")
        return {"success": False, "message": "发送验证码失败，请稍后重试"}

@app.post("/api/auth/reset-password")
async def reset_password(request: Request):
    """重置密码"""
    try:
        data = await request.json()
        email = data.get('email', '').strip()
        verification_code = data.get('verification_code', '').strip()
        new_password = data.get('new_password', '').strip()
        
        if not all([email, verification_code, new_password]):
            return {"success": False, "message": "请填写所有必填字段"}
        
        # 验证密码长度
        if len(new_password) < 6:
            return {"success": False, "message": "密码长度至少6位"}
        
        # 验证验证码
        if not db.verify_email_code(email, verification_code, "password_reset"):
            return {"success": False, "message": "验证码错误或已过期"}
        
        # 重置密码
        success = db.reset_user_password(email, new_password)
        
        if success:
            return {"success": True, "message": "密码重置成功"}
        else:
            return {"success": False, "message": "密码重置失败，请稍后重试"}
            
    except Exception as e:
        print(f"重置密码失败: {e}")
        return {"success": False, "message": "密码重置失败，请稍后重试"}

@app.get("/email-config", response_class=HTMLResponse)
async def email_config_page():
    """邮件配置页面"""
    try:
        template_path = os.path.join(os.path.dirname(__file__), "templates", "email_config.html")
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        return HTMLResponse(content=f"<h1>页面加载错误</h1><p>{str(e)}</p>", status_code=500)

@app.get("/test-photo", response_class=HTMLResponse)
async def test_photo_page():
    """照片测试页面"""
    try:
        template_path = os.path.join(os.path.dirname(__file__), "templates", "test_photo.html")
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        return HTMLResponse(content=f"<h1>页面加载错误</h1><p>{str(e)}</p>", status_code=500)

# 新增功能API端点
@app.post("/api/message")
async def add_message(
    memorial_id: str = Form(...),
    visitor_name: str = Form(...),
    message: str = Form(...)
):
    """添加访客留言"""
    try:
        # 通过纪念馆ID获取宠物ID
        pet_info = db.get_pet_by_memorial_id(memorial_id)
        if not pet_info:
            return {"success": False, "error": "纪念馆不存在"}
        
        pet_id = pet_info[0]  # 第一列是id
        db.save_message(pet_id, visitor_name, message)
        
        return {"success": True, "message": "留言添加成功"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/messages/{memorial_id}")
async def get_messages(memorial_id: str):
    """获取纪念馆的所有留言"""
    try:
        pet_info = db.get_pet_by_memorial_id(memorial_id)
        if not pet_info:
            return {"success": False, "error": "纪念馆不存在"}
        
        pet_id = pet_info[0]
        messages = db.get_messages(pet_id)
        
        # 格式化留言数据
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "visitor_name": msg[0],
                "message": msg[1],
                "created_at": msg[2]
            })
        
        return {"success": True, "messages": formatted_messages}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/reminder")
async def add_reminder(
    memorial_id: str = Form(...),
    reminder_type: str = Form(...),
    reminder_date: str = Form(...),
    custom_name: str = Form(None),
    custom_description: str = Form(None)
):
    """添加纪念日提醒"""
    try:
        pet_info = db.get_pet_by_memorial_id(memorial_id)
        if not pet_info:
            return {"success": False, "error": "纪念馆不存在"}
        
        pet_id = pet_info[0]
        db.save_reminder(pet_id, reminder_type, reminder_date, custom_name, custom_description)
        
        return {"success": True, "message": "提醒添加成功"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/reminders/{memorial_id}")
async def get_reminders(memorial_id: str):
    """获取纪念馆的所有提醒"""
    try:
        pet_info = db.get_pet_by_memorial_id(memorial_id)
        if not pet_info:
            return {"success": False, "error": "纪念馆不存在"}
        
        pet_id = pet_info[0]
        reminders = db.get_reminders(pet_id)
        
        formatted_reminders = []
        for reminder in reminders:
            formatted_reminders.append({
                "id": reminder[0],  # 添加ID字段
                "type": reminder[1],
                "date": reminder[2],
                "custom_name": reminder[3],
                "custom_description": reminder[4],
                "is_active": reminder[5]
            })
        
        return {"success": True, "reminders": formatted_reminders}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.delete("/api/reminder/{reminder_id}")
async def delete_reminder(reminder_id: int):
    """删除指定的提醒"""
    try:
        success = db.delete_reminder(reminder_id)
        if success:
            return {"success": True, "message": "提醒删除成功"}
        else:
            return {"success": False, "error": "提醒不存在或删除失败"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# 心情日记API
@app.post("/api/mood-diary")
async def add_mood_diary(
    memorial_id: str = Form(...),
    mood_type: str = Form(...),
    mood_score: int = Form(...),
    diary_content: str = Form(...),
    weather: str = Form("")
):
    """添加心情日记"""
    try:
        pet_info = db.get_pet_by_memorial_id(memorial_id)
        if not pet_info:
            return {"success": False, "error": "纪念馆不存在"}
        
        pet_id = pet_info[0]
        db.save_mood_diary(pet_id, mood_type, mood_score, diary_content, weather)
        
        return {"success": True, "message": "心情日记添加成功"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/mood-diaries/{memorial_id}")
async def get_mood_diaries(memorial_id: str):
    """获取纪念馆的心情日记"""
    try:
        pet_info = db.get_pet_by_memorial_id(memorial_id)
        if not pet_info:
            return {"success": False, "error": "纪念馆不存在"}
        
        pet_id = pet_info[0]
        diaries = db.get_mood_diaries(pet_id)
        
        formatted_diaries = []
        for diary in diaries:
            formatted_diaries.append({
                "mood_type": diary[0],
                "mood_score": diary[1],
                "diary_content": diary[2],
                "weather": diary[3],
                "created_at": diary[4]
            })
        
        return {"success": True, "diaries": formatted_diaries}
    except Exception as e:
        return {"success": False, "error": str(e)}

# 访问统计API
@app.post("/api/visit-stat")
async def record_visit(
    memorial_id: str = Form(...),
    request: Request = None
):
    """记录访问统计"""
    try:
        client_ip = request.client.host if request else "unknown"
        user_agent = request.headers.get("user-agent", "unknown") if request else "unknown"
        
        db.save_visit_stat(memorial_id, client_ip, user_agent)
        return {"success": True, "message": "访问记录成功"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/visit-stats/{memorial_id}")
async def get_visit_stats(memorial_id: str):
    """获取纪念馆访问统计"""
    try:
        stats = db.get_visit_stats(memorial_id)
        if stats:
            return {
                "success": True,
                "stats": {
                    "total_visits": stats[0],
                    "unique_visitors": stats[1],
                    "last_visit": stats[2]
                }
            }
        else:
            return {
                "success": True,
                "stats": {
                    "total_visits": 0,
                    "unique_visitors": 0,
                    "last_visit": None
                }
            }
    except Exception as e:
        return {"success": False, "error": str(e)}



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)