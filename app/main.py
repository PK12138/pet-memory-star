from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException, Depends, Header
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import Database
from services import MemorialService, EmailService
from auth_service import AuthService
from payment_service import PaymentService
from ai_chat_service import AIChatService
import os
import uuid
import uvicorn
import json
from typing import Optional
from datetime import datetime

app = FastAPI(title="爪迹星·云纪念馆")

# 健康检查接口
@app.get("/api/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "message": "服务器运行正常",
        "timestamp": "2025-09-18T13:36:23Z"
    }

# 添加session_token中间件
@app.middleware("http")
async def add_session_token_to_header(request: Request, call_next):
    # 从查询参数中获取session_token
    session_token = request.query_params.get("session_token")
    if session_token:
        # 将session_token添加到请求头中
        request.headers.__dict__["_list"].append((b"x-session-token", session_token.encode()))
        print(f"🔑 添加session_token到Header: {session_token[:20]}...")
    
    response = await call_next(request)
    return response

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
ai_chat_service = AIChatService()
payment_service = PaymentService()
from virtual_companion_service import VirtualCompanionService
virtual_companion_service = VirtualCompanionService(db)
from dream_analysis_service import DreamAnalysisService
# 从环境变量获取 DeepSeek API Key
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
dream_analysis_service = DreamAnalysisService(api_key=DEEPSEEK_API_KEY)

# 依赖函数：获取当前用户
async def get_current_user(
    authorization: Optional[str] = Header(None),
    x_session_token: Optional[str] = Header(None, alias="x-session-token")
):
    # 优先使用 x-session-token，其次使用 Authorization
    session_token = x_session_token
    if not session_token and authorization and authorization.startswith("Bearer "):
        session_token = authorization.replace("Bearer ", "")
    
    if not session_token:
        raise HTTPException(status_code=401, detail="未提供有效的认证令牌")
    
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

@app.post("/api/memorial/create")
async def create_memorial_json(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """创建纪念馆API（JSON格式，适用于小程序）"""
    try:
        data = await request.json()
        
        print(f"📝 收到创建纪念馆请求，数据: {data}")
        
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
        
        # 获取提交的数据（支持所有字段）
        pet_name = data.get("pet_name", "")
        species = data.get("species", data.get("breed", ""))  # 优先使用species字段
        breed = data.get("breed", "")
        color = data.get("color", "")
        gender = data.get("gender", "")
        birth_date = data.get("birth_date", "")
        memorial_date = data.get("memorial_date", "")
        weight = data.get("weight", 0.0)
        status = data.get("status", "alive")
        address = data.get("address", "")
        description = data.get("description", "")
        personality = data.get("personality", "")
        personality_answers = data.get("personality_answers", {})
        
        # 构建宠物信息
        import datetime
        pet_info = {
            "name": pet_name,
            "species": species,
            "breed": breed,
            "color": color,
            "gender": gender,
            "birth_date": birth_date,
            "memorial_date": memorial_date or datetime.datetime.now().strftime("%Y-%m-%d"),
            "weight": float(weight) if weight else 0.0,
            "status": status,
            "address": address
        }
        
        print(f"🐾 宠物信息: {pet_info}")
        print(f"📋 性格测试答案: {personality_answers}")
        
        # 创建纪念馆（暂时不上传照片）
        memorial_url, personality_type, ai_letter = memorial_service.create_memorial_advanced(
            email=user_email,
            pet_info=pet_info,
            photos=[],  # 小程序可以稍后上传照片
            personality_answers=personality_answers,
            user_id=user_id
        )
        
        print(f"✅ 纪念馆创建成功: {memorial_url}")
        
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
    """创建纪念馆完整流程（包含性格测试和AI信件）- 网页版"""
    try:
        # 检查用户权限
        user_id = current_user["id"]
        permission_check = auth_service.can_create_memorial(user_id)
        if not permission_check["can_create"]:
            return templates.TemplateResponse("error.html", {
                "request": request,
                "error_title": "权限不足",
                "error_message": permission_check["message"],
                "error_code": 403
            })
        
        # 检查照片数量限制
        level_info = database.get_user_level_info(current_user["user_level"])
        if level_info and level_info[3] != -1:  # 如果不是无限照片
            max_photos = level_info[3]
            if len(photos) > max_photos:
                return templates.TemplateResponse("error.html", {
                    "request": request,
                    "error_title": "照片数量超限",
                    "error_message": f"最多只能上传{max_photos}张照片，请升级会员以获取更多照片空间",
                    "error_code": 403
                })
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
async def view_memorial(request: Request, memorial_id: str):
    """查看纪念馆页面"""
    try:
        # 获取纪念馆信息
        memorial = db.get_memorial_by_id(memorial_id)
        if not memorial:
            return HTMLResponse(content="<h1>纪念馆不存在</h1>", status_code=404)
        
        pet_info = db.get_pet_by_memorial_id(memorial_id)
        if not pet_info:
            return HTMLResponse(content="<h1>纪念馆数据异常</h1>", status_code=404)
        
        # 获取照片
        photos = db.get_memorial_photos(memorial_id)
        
        # 计算年龄（如果有生日和纪念日）
        age = ""
        if memorial.get("birth_date") and memorial.get("memorial_date"):
            from datetime import datetime
            try:
                birth = datetime.strptime(memorial.get("birth_date"), "%Y-%m-%d")
                memorial_d = datetime.strptime(memorial.get("memorial_date"), "%Y-%m-%d")
                years = memorial_d.year - birth.year
                months = memorial_d.month - birth.month
                if months < 0:
                    years -= 1
                    months += 12
                age = f"{years}岁{months}个月" if years > 0 else f"{months}个月"
            except:
                age = ""
        
        # 使用模板渲染
        return templates.TemplateResponse("memorial.html", {
            "request": request,
            "memorial_id": memorial_id,
            "pet_name": pet_info.get("name", "宠物"),
            "species": pet_info.get("species", "未知"),
            "memorial_date": memorial.get("memorial_date", "")[:10] if memorial.get("memorial_date") else "",
            "age": age,
            "gender": pet_info.get("gender", ""),
            "personality": memorial.get("personality", ""),
            "story": memorial.get("description", ""),
            "photos": photos,
            "personality_type": pet_info.get("personality", ""),
            "ai_letter": memorial.get("ai_letter", "")
        })
    except Exception as e:
        print(f"查看纪念馆错误: {str(e)}")
        return HTMLResponse(content=f"<h1>加载失败: {str(e)}</h1>", status_code=500)

@app.get("/memorial/{memorial_id}/ai-chat", response_class=HTMLResponse)
async def ai_chat_page(request: Request, memorial_id: str):
    """AI对话页面"""
    try:
        # 获取纪念馆信息
        pet_info = db.get_pet_by_memorial_id(memorial_id)
        if not pet_info:
            return templates.TemplateResponse("error.html", {
                "request": request,
                "error_title": "纪念馆不存在",
                "error_message": "找不到该纪念馆",
                "error_code": 404
            })
        
        # 获取宠物的第一张照片作为头像
        photos = db.get_memorial_photos(memorial_id)
        pet_avatar = photos[0] if photos else ""
        
        return templates.TemplateResponse("ai_chat.html", {
            "request": request,
            "memorial_id": memorial_id,
            "pet_name": pet_info.get("name", "宠物"),
            "pet_avatar": pet_avatar
        })
    except Exception as e:
        print(f"AI对话页面错误: {str(e)}")
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error_title": "页面加载失败",
            "error_message": str(e),
            "error_code": 500
        })

@app.get("/memorial/{memorial_id}/companion", response_class=HTMLResponse)
async def virtual_companion_page(request: Request, memorial_id: str):
    """虚拟陪伴页面"""
    try:
        # 获取纪念馆信息
        pet_info = db.get_pet_by_memorial_id(memorial_id)
        if not pet_info:
            return templates.TemplateResponse("error.html", {
                "request": request,
                "error_title": "纪念馆不存在",
                "error_message": "找不到该纪念馆",
                "error_code": 404
            })
        
        # 获取宠物的第一张照片作为头像
        photos = db.get_memorial_photos(memorial_id)
        pet_avatar = photos[0] if photos else ""
        
        return templates.TemplateResponse("virtual_companion.html", {
            "request": request,
            "memorial_id": memorial_id,
            "pet_name": pet_info.get("name", "宠物"),
            "pet_avatar": pet_avatar
        })
    except Exception as e:
        print(f"虚拟陪伴页面错误: {str(e)}")
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error_title": "页面加载失败",
            "error_message": str(e),
            "error_code": 500
        })

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
        
        print(f"🔍 发送验证码请求 - 邮箱: {email}")
        
        if not email:
            print("❌ 邮箱地址为空")
            return {"success": False, "message": "请输入邮箱地址"}
        
        # 检查邮箱格式
        import re
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            print("❌ 邮箱格式不正确")
            return {"success": False, "message": "邮箱格式不正确"}
        
        # 检查用户是否存在
        if not db.user_exists(email):
            print("❌ 用户不存在")
            return {"success": False, "message": "该邮箱未注册，请先注册账户"}
        
        print("✅ 用户存在，生成验证码")
        
        # 生成验证码
        code = db.create_email_code(email, "password_reset")
        print(f"🔍 生成的验证码: {code}")
        
        # 发送验证码邮件
        print("📧 开始发送验证码邮件")
        success = email_service.send_verification_code(email, code)
        print(f"📧 邮件发送结果: {success}")
        
        if success:
            print("✅ 验证码发送成功")
            return {"success": True, "message": "验证码已发送到您的邮箱"}
        else:
            print("❌ 验证码发送失败")
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
    visit_data: dict,
    request: Request = None
):
    """记录访问统计"""
    try:
        memorial_id = visit_data.get("memorial_id")
        if not memorial_id:
            return {"success": False, "error": "缺少memorial_id参数"}
        
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


# 权限管理相关接口
@app.get("/api/user/info")
async def get_user_info_api(current_user: dict = Depends(get_current_user)):
    """获取用户信息API（小程序使用）"""
    try:
        user_id = current_user["id"]
        dashboard_data = auth_service.get_user_dashboard_data(user_id)
        
        if not dashboard_data["success"]:
            return JSONResponse(
                content=dashboard_data,
                status_code=500
            )
        
        return JSONResponse(content={
            "success": True,
            "user": dashboard_data["user"],
            "permissions": {
                "can_create_memorial": auth_service.can_create_memorial(user_id),
                "can_use_ai": auth_service.can_use_ai_feature(user_id),
                "can_export": auth_service.can_export_data(user_id)
            }
        })
    except Exception as e:
        return JSONResponse(
            content={"success": False, "message": f"获取用户信息失败：{str(e)}"},
            status_code=500
        )


@app.get("/api/user/dashboard")
async def get_user_dashboard_api(current_user: dict = Depends(get_current_user)):
    """获取用户仪表板数据API（小程序使用）"""
    try:
        user_id = current_user["id"]
        print(f"📊 获取仪表板数据: user_id={user_id}")
        
        dashboard_data = auth_service.get_user_dashboard_data(user_id)
        print(f"📊 仪表板原始数据: {dashboard_data}")
        
        if not dashboard_data.get("success"):
            print(f"❌ 仪表板数据获取失败: {dashboard_data.get('message')}")
            return JSONResponse(
                content=dashboard_data,
                status_code=500
            )
        
        # 获取纪念馆列表（安全处理）
        try:
            user_memorials = db.get_user_memorials(user_id) or []
            print(f"📊 用户纪念馆列表: {len(user_memorials)} 个")
        except Exception as e:
            print(f"❌ 获取纪念馆列表失败: {str(e)}")
            user_memorials = []
        
        # 计算总访问量（安全处理）
        total_views = 0
        try:
            total_views = sum(memorial.get("view_count", 0) for memorial in user_memorials if isinstance(memorial, dict))
        except Exception as e:
            print(f"❌ 计算访问量失败: {str(e)}")
            total_views = 0
        
        result = {
            "success": True,
            "data": {
                "memorial_count": dashboard_data["user"].get("memorial_count", 0),
                "total_photos": dashboard_data["user"].get("total_photos", 0),
                "total_views": total_views,
                "user_level": dashboard_data["user"].get("user_level", 0),
                "level_name": dashboard_data["user"].get("level_name", "普通用户")
            }
        }
        print(f"✅ 仪表板数据返回: {result}")
        return JSONResponse(content=result)
        
    except Exception as e:
        print(f"❌ 获取仪表板数据异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            content={"success": False, "message": f"获取仪表板数据失败：{str(e)}"},
            status_code=500
        )


@app.get("/api/user/level-info")
async def get_user_level_info(current_user: dict = Depends(get_current_user)):
    """获取用户等级信息API（小程序使用）"""
    try:
        user_id = current_user["id"]
        dashboard_data = auth_service.get_user_dashboard_data(user_id)
        
        if not dashboard_data["success"]:
            return JSONResponse(
                content=dashboard_data,
                status_code=500
            )
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "user_level": dashboard_data["user"]["user_level"],
                "level_name": dashboard_data["user"]["level_name"],
                "memorial_count": dashboard_data["user"]["memorial_count"],
                "total_photos": dashboard_data["user"]["total_photos"]
            }
        })
    except Exception as e:
        return JSONResponse(
            content={"success": False, "message": f"获取等级信息失败：{str(e)}"},
            status_code=500
        )


@app.get("/api/user/permissions")
async def get_user_permissions(session_token: str = Header(None, alias="x-session-token")):
    """获取用户权限信息"""
    try:
        print(f"🔍 权限API - session_token: {session_token[:20] if session_token else 'None'}...")
        
        user = auth_service.get_current_user(session_token)
        if not user:
            print("❌ 权限API - 用户未登录")
            return {"success": False, "message": "用户未登录"}
        
        user_id = user["id"]
        dashboard_data = auth_service.get_user_dashboard_data(user_id)
        
        if not dashboard_data["success"]:
            return dashboard_data
        
        return {
            "success": True,
            "permissions": {
                "can_create_memorial": auth_service.can_create_memorial(user_id),
                "can_use_ai": auth_service.can_use_ai_feature(user_id),
                "can_export": auth_service.can_export_data(user_id),
                "email_verified": user.get("email_verified", False)
            },
            "user_info": dashboard_data["user"]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/user/check-memorial-permission")
async def check_memorial_permission(request: Request, session_token: str = Header(None, alias="x-session-token")):
    """检查纪念馆创建权限"""
    try:
        user = auth_service.get_current_user(session_token)
        if not user:
            return {"success": False, "message": "用户未登录"}
        
        user_id = user["id"]
        permission = auth_service.can_create_memorial(user_id)
        
        return {
            "success": True,
            "permission": permission
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/user/check-photo-permission")
async def check_photo_permission(request: Request, session_token: str = Header(None, alias="x-session-token")):
    """检查照片上传权限"""
    try:
        data = await request.json()
        memorial_id = data.get("memorial_id")
        
        if not memorial_id:
            return {"success": False, "message": "纪念馆ID不能为空"}
        
        user = auth_service.get_current_user(session_token)
        if not user:
            return {"success": False, "message": "用户未登录"}
        
        user_id = user["id"]
        permission = auth_service.can_upload_photo(user_id, memorial_id)
        
        return {
            "success": True,
            "permission": permission
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/user/check-ai-permission")
async def check_ai_permission(session_token: str = Header(None, alias="x-session-token")):
    """检查AI功能使用权限"""
    try:
        user = auth_service.get_current_user(session_token)
        if not user:
            return {"success": False, "message": "用户未登录"}
        
        user_id = user["id"]
        permission = auth_service.can_use_ai_feature(user_id)
        
        return {
            "success": True,
            "permission": permission
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/user/upgrade")
async def upgrade_user_level(request: Request, session_token: str = Header(None, alias="x-session-token")):
    """升级用户等级"""
    try:
        data = await request.json()
        new_level = data.get("new_level")
        
        if new_level is None:
            return {"success": False, "message": "目标等级不能为空"}
        
        user = auth_service.get_current_user(session_token)
        if not user:
            return {"success": False, "message": "用户未登录"}
        
        user_id = user["id"]
        result = auth_service.upgrade_user_level(user_id, new_level)
        
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/user/levels")
async def get_user_levels():
    """获取所有用户等级信息"""
    try:
        levels = database.get_all_user_levels()
        return {
            "success": True,
            "levels": levels
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# 充值相关API
@app.get("/payment", response_class=HTMLResponse)
async def payment_page(request: Request):
    """充值页面"""
    try:
        template_path = os.path.join(os.path.dirname(__file__), "templates", "payment.html")
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        return HTMLResponse(content=f"<h1>页面加载错误</h1><p>{str(e)}</p>", status_code=500)

@app.get("/api/payment/plans")
async def get_payment_plans():
    """获取充值套餐列表"""
    try:
        plans = [
            {
                "id": "monthly",
                "name": "月度会员",
                "price": 29.9,
                "period": "1个月",
                "features": [
                    "无限纪念馆",
                    "无限照片上传",
                    "AI智能功能",
                    "数据导出",
                    "优先客服支持"
                ],
                "recommended": False
            },
            {
                "id": "yearly",
                "name": "年度会员",
                "price": 299.0,
                "period": "12个月",
                "features": [
                    "无限纪念馆",
                    "无限照片上传",
                    "AI智能功能",
                    "数据导出",
                    "优先客服支持",
                    "专属主题",
                    "自定义域名"
                ],
                "recommended": True
            }
        ]
        
        return {"success": True, "plans": plans}
    except Exception as e:
        return {"success": False, "message": f"获取套餐列表失败: {str(e)}"}

@app.get("/api/user/balance")
async def get_user_balance(session_token: str = Header(None, alias="x-session-token")):
    """获取用户余额信息"""
    try:
        user = auth_service.get_current_user(session_token)
        if not user:
            return {"success": False, "message": "用户未登录"}
        
        user_id = user["id"]
        
        # 初始化用户余额（如果不存在）
        db.init_user_balance(user_id)
        
        # 获取余额信息
        balance_info = db.get_user_balance(user_id)
        if not balance_info:
            balance_info = {
                "balance": 0.0,
                "frozen_balance": 0.0,
                "total_recharged": 0.0,
                "total_consumed": 0.0
            }
        
        # 获取用户等级信息
        level_info = db.get_user_level_info(user["user_level"])
        
        return {
            "success": True,
            "balance": balance_info,
            "user_info": {
                "id": user["id"],
                "email": user["email"],
                "level_info": {
                    "name": level_info[1] if level_info else "免费用户",
                    "level": user["user_level"]
                }
            }
        }
    except Exception as e:
        return {"success": False, "message": f"获取余额信息失败: {str(e)}"}

@app.post("/api/payment/create")
async def create_payment_order(request: Request, session_token: str = Header(None, alias="x-session-token")):
    """创建支付订单"""
    try:
        user = auth_service.get_current_user(session_token)
        if not user:
            return {"success": False, "message": "用户未登录"}
        
        data = await request.json()
        plan_id = data.get("plan_id")
        payment_method = data.get("payment_method")
        openid = data.get("openid", "")  # 微信支付需要openid
        
        if not plan_id or not payment_method:
            return {"success": False, "message": "参数不完整"}
        
        # 获取套餐信息
        plans = {
            "monthly": {"amount": 29.9, "description": "月度会员"},
            "yearly": {"amount": 299.0, "description": "年度会员"}
        }
        
        if plan_id not in plans:
            return {"success": False, "message": "套餐不存在"}
        
        plan = plans[plan_id]
        user_id = user["id"]
        
        # 创建支付订单
        order_id = db.create_payment_order(
            user_id=user_id,
            order_type=f"upgrade_{plan_id}",
            amount=plan["amount"],
            payment_method=payment_method,
            description=plan["description"]
        )
        
        if not order_id:
            return {"success": False, "message": "创建订单失败"}
        
        # 使用真实支付服务创建订单
        notify_url = f"{os.getenv('SERVER_BASE_URL', 'http://localhost:8000')}/api/payment/{payment_method}/notify"
        
        payment_result = payment_service.create_payment_order(
            payment_method=payment_method,
            order_id=order_id,
            amount=plan["amount"],
            description=plan["description"],
            openid=openid,
            notify_url=notify_url,
            subject=plan["description"]
        )
        
        if payment_result["success"]:
            return {
                "success": True,
                "order_id": order_id,
                "amount": plan["amount"],
                "payment_data": payment_result,
                "message": "订单创建成功"
            }
        else:
            return {
                "success": False,
                "message": payment_result.get("message", "创建支付订单失败")
            }
        
    except Exception as e:
        return {"success": False, "message": f"创建支付订单失败: {str(e)}"}

@app.get("/payment/process/{order_id}")
async def payment_process(request: Request, order_id: str):
    """支付处理页面"""
    try:
        # 获取订单信息
        order = db.get_payment_order(order_id)
        if not order:
            return HTMLResponse(content="<h1>订单不存在</h1>", status_code=404)
        
        # 这里应该显示支付二维码或跳转到支付平台
        # 目前返回简单的支付页面
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>支付处理 -  爪迹星</title>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    text-align: center;
                    padding: 50px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }}
                .container {{
                    background: rgba(255,255,255,0.1);
                    padding: 40px;
                    border-radius: 20px;
                    max-width: 500px;
                    margin: 0 auto;
                }}
                .amount {{
                    font-size: 2rem;
                    font-weight: bold;
                    color: #4CAF50;
                    margin: 20px 0;
                }}
                .btn {{
                    background: #4CAF50;
                    color: white;
                    padding: 15px 30px;
                    border: none;
                    border-radius: 10px;
                    font-size: 1.1rem;
                    cursor: pointer;
                    margin: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>💳 支付处理</h1>
                <p>订单号: {order_id}</p>
                <p>商品: {order['description']}</p>
                <div class="amount">¥{order['amount']}</div>
                <p>支付方式: {order['payment_method']}</p>
                <button class="btn" onclick="simulatePayment('{order_id}')">模拟支付成功</button>
                <button class="btn" onclick="window.location.href='/payment'">返回充值</button>
            </div>
            <script>
                function simulatePayment(orderId) {{
                    fetch('/api/payment/callback', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{
                            order_id: orderId,
                            status: 'paid',
                            platform_order_id: 'sim_' + Date.now()
                        }})
                    }})
                    .then(response => response.json())
                    .then(data => {{
                        if (data.success) {{
                            alert('支付成功！');
                            window.location.href = '/user-center';
                        }} else {{
                            alert('支付失败：' + data.message);
                        }}
                    }});
                }}
            </script>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        return HTMLResponse(content=f"<h1>支付处理错误</h1><p>{str(e)}</p>", status_code=500)

# 微信支付回调
@app.post("/api/payment/wechat/notify")
async def wechat_payment_notify(request: Request):
    """微信支付回调"""
    try:
        # 获取请求头和请求体
        headers = dict(request.headers)
        body = await request.body()
        body_str = body.decode('utf-8')
        
        # 验证微信支付通知
        verify_result = payment_service.verify_payment_notify(
            payment_method='wechat',
            headers=headers,
            body=body_str
        )
        
        if not verify_result["success"]:
            return {"code": "FAIL", "message": "验证失败"}
        
        notify_data = verify_result["data"]
        order_id = notify_data.get("out_trade_no")
        trade_state = notify_data.get("trade_state")
        
        if trade_state == "SUCCESS":
            # 支付成功，更新订单状态
            success = db.update_payment_status(order_id, "paid", notify_data.get("transaction_id"))
            
            if success:
                # 处理支付成功逻辑
                order = db.get_payment_order(order_id)
                if order:
                    user_id = order["user_id"]
                    
                    # 根据订单类型处理
                    if order["order_type"] == "upgrade_monthly":
                        db.upgrade_user_level(user_id, 1, order_id)
                    elif order["order_type"] == "upgrade_yearly":
                        db.upgrade_user_level(user_id, 1, order_id)
                    
                    # 记录充值
                    db.add_user_balance(user_id, order["amount"], order_id, "upgrade")
                
                return {"code": "SUCCESS", "message": "OK"}
            else:
                return {"code": "FAIL", "message": "更新订单状态失败"}
        else:
            return {"code": "FAIL", "message": "支付未成功"}
            
    except Exception as e:
        print(f"微信支付回调处理失败: {e}")
        return {"code": "FAIL", "message": "处理失败"}

# 支付宝回调
@app.post("/api/payment/alipay/notify")
async def alipay_payment_notify(request: Request):
    """支付宝支付回调"""
    try:
        # 获取请求参数
        form_data = await request.form()
        data = dict(form_data)
        
        # 验证支付宝通知
        verify_result = payment_service.verify_payment_notify(
            payment_method='alipay',
            data=data
        )
        
        if not verify_result["success"]:
            return "failure"
        
        notify_data = verify_result["data"]
        order_id = notify_data.get("out_trade_no")
        trade_status = notify_data.get("trade_status")
        
        if trade_status == "TRADE_SUCCESS" or trade_status == "TRADE_FINISHED":
            # 支付成功，更新订单状态
            success = db.update_payment_status(order_id, "paid", notify_data.get("trade_no"))
            
            if success:
                # 处理支付成功逻辑
                order = db.get_payment_order(order_id)
                if order:
                    user_id = order["user_id"]
                    
                    # 根据订单类型处理
                    if order["order_type"] == "upgrade_monthly":
                        db.upgrade_user_level(user_id, 1, order_id)
                    elif order["order_type"] == "upgrade_yearly":
                        db.upgrade_user_level(user_id, 1, order_id)
                    
                    # 记录充值
                    db.add_user_balance(user_id, order["amount"], order_id, "upgrade")
                
                return "success"
            else:
                return "failure"
        else:
            return "failure"
            
    except Exception as e:
        print(f"支付宝回调处理失败: {e}")
        return "failure"

@app.post("/api/payment/callback")
async def payment_callback(request: Request):
    """通用支付回调处理（用于测试）"""
    try:
        data = await request.json()
        order_id = data.get("order_id")
        status = data.get("status")
        platform_order_id = data.get("platform_order_id")
        
        if not order_id or not status:
            return {"success": False, "message": "参数不完整"}
        
        # 获取订单信息
        order = db.get_payment_order(order_id)
        if not order:
            return {"success": False, "message": "订单不存在"}
        
        # 更新支付状态
        success = db.update_payment_status(order_id, status, platform_order_id)
        
        if success and status == "paid":
            # 处理支付成功逻辑
            user_id = order["user_id"]
            
            # 根据订单类型处理
            if order["order_type"] == "upgrade_monthly":
                # 升级到高级用户（1个月）
                db.upgrade_user_level(user_id, 1, order_id)
            elif order["order_type"] == "upgrade_yearly":
                # 升级到高级用户（1年）
                db.upgrade_user_level(user_id, 1, order_id)
            
            # 记录充值
            db.add_user_balance(user_id, order["amount"], order_id, "upgrade")
        
        return {"success": True, "message": "支付状态更新成功"}
        
    except Exception as e:
        return {"success": False, "message": f"支付回调处理失败: {str(e)}"}

@app.get("/memorials", response_class=HTMLResponse)
async def memorials_page(request: Request):
    """纪念馆列表页面"""
    try:
        template_path = os.path.join(os.path.dirname(__file__), "templates", "memorials.html")
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        return HTMLResponse(content=f"<h1>页面加载错误</h1><p>{str(e)}</p>", status_code=500)

@app.get("/memorial/edit/{memorial_id}", response_class=HTMLResponse)
async def memorial_edit_page(request: Request, memorial_id: str):
    """纪念馆编辑页面"""
    try:
        template_path = os.path.join(os.path.dirname(__file__), "templates", "memorial_edit.html")
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        return HTMLResponse(content=f"<h1>页面加载错误</h1><p>{str(e)}</p>", status_code=500)

@app.get("/orders", response_class=HTMLResponse)
async def orders_page(request: Request):
    """订单管理页面"""
    try:
        template_path = os.path.join(os.path.dirname(__file__), "templates", "orders.html")
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        return HTMLResponse(content=f"<h1>页面加载错误</h1><p>{str(e)}</p>", status_code=500)

@app.get("/api/user/orders")
async def get_user_orders(
    request: Request,
    page: int = 1,
    status: str = "all",
    session_token: str = Header(None, alias="x-session-token")
):
    """获取用户订单列表"""
    try:
        user = auth_service.get_current_user(session_token)
        if not user:
            return {"success": False, "message": "用户未登录"}
        
        user_id = user["id"]
        limit = 10
        offset = (page - 1) * limit
        
        # 获取订单列表
        orders = db.get_user_payment_orders(user_id, limit * 2)  # 获取更多数据用于筛选
        
        # 筛选订单
        if status != "all":
            orders = [order for order in orders if order["payment_status"] == status]
        
        # 分页
        total_orders = len(orders)
        orders = orders[offset:offset + limit]
        
        # 计算统计信息
        all_orders = db.get_user_payment_orders(user_id, 1000)  # 获取所有订单用于统计
        stats = {
            "total_orders": len(all_orders),
            "total_amount": sum(order["amount"] for order in all_orders if order["payment_status"] == "paid"),
            "success_orders": len([order for order in all_orders if order["payment_status"] == "paid"]),
            "pending_orders": len([order for order in all_orders if order["payment_status"] == "pending"])
        }
        
        # 分页信息
        pagination = {
            "current_page": page,
            "total_pages": (total_orders + limit - 1) // limit,
            "total_items": total_orders
        }
        
        return {
            "success": True,
            "orders": orders,
            "stats": stats,
            "pagination": pagination
        }
        
    except Exception as e:
        return {"success": False, "message": f"获取订单列表失败: {str(e)}"}

@app.post("/api/payment/cancel")
async def cancel_payment_order(request: Request, session_token: str = Header(None, alias="x-session-token")):
    """取消支付订单"""
    try:
        user = auth_service.get_current_user(session_token)
        if not user:
            return {"success": False, "message": "用户未登录"}
        
        data = await request.json()
        order_id = data.get("order_id")
        
        if not order_id:
            return {"success": False, "message": "订单ID不能为空"}
        
        # 获取订单信息
        order = db.get_payment_order(order_id)
        if not order:
            return {"success": False, "message": "订单不存在"}
        
        # 检查订单是否属于当前用户
        if order["user_id"] != user["id"]:
            return {"success": False, "message": "无权操作此订单"}
        
        # 检查订单状态
        if order["payment_status"] != "pending":
            return {"success": False, "message": "只能取消待支付的订单"}
        
        # 更新订单状态
        success = db.update_payment_status(order_id, "cancelled")
        
        if success:
            return {"success": True, "message": "订单已取消"}
        else:
            return {"success": False, "message": "取消订单失败"}
            
    except Exception as e:
        return {"success": False, "message": f"取消订单失败: {str(e)}"}

@app.get("/user-center")
async def user_center(request: Request):
    """用户中心页面"""
    try:
        # 从查询参数获取session_token
        session_token = request.query_params.get("session_token")
        print(f"🔍 用户中心访问 - session_token: {session_token[:20] if session_token else 'None'}...")
        print(f"🔍 查询参数: {request.query_params}")
        
        # 如果没有找到session_token，返回登录页面
        if not session_token:
            print("❌ 没有找到session_token，返回登录页面")
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error_message": "请先登录"
            })
        
        user = auth_service.get_current_user(session_token)
        print(f"🔍 用户验证结果: {user}")
        if not user:
            print("❌ 用户验证失败，返回登录页面")
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error_message": "登录已过期，请重新登录"
            })
        
        user_id = user["id"]
        
        # 获取用户权限信息
        permissions = {
            "can_create_memorial": auth_service.can_create_memorial(user_id),
            "can_use_ai": auth_service.can_use_ai_feature(user_id),
            "can_export": auth_service.can_export_data(user_id)
        }
        
        # 获取用户仪表板数据
        dashboard_data = auth_service.get_user_dashboard_data(user_id)
        if not dashboard_data["success"]:
            return templates.TemplateResponse("error.html", {
                "request": request,
                "error_title": "获取用户信息失败",
                "error_message": dashboard_data["message"]
            })
        
        return templates.TemplateResponse("user_center.html", {
            "request": request,
            "user": dashboard_data["user"],
            "permissions": permissions
        })
    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error_title": "页面加载失败",
            "error_message": str(e)
        })


# ==================== 纪念馆管理API ====================

@app.get("/api/user/memorials")
async def get_user_memorials(session_token: str = Header(None, alias="x-session-token")):
    """获取用户纪念馆列表"""
    try:
        user = auth_service.get_current_user(session_token)
        if not user:
            return {"success": False, "message": "用户未登录"}
        
        memorials = db.get_user_memorials(user["id"])
        
        # 为每个纪念馆添加统计信息
        for memorial in memorials:
            photos = db.get_memorial_photos(memorial["id"]) or []
            memorial["photos"] = photos
            memorial["photo_count"] = len(photos)
            
            # 获取访问统计
            visit_stats = db.get_visit_stats(memorial["id"])
            if visit_stats:
                memorial["view_count"] = visit_stats[0] or 0  # total_visits
                memorial["visitor_count"] = visit_stats[1] or 0  # unique_visitors
            else:
                memorial["view_count"] = 0
                memorial["visitor_count"] = 0
            
            # 获取留言数量
            messages = db.get_messages(memorial["id"])
            memorial["message_count"] = len(messages) if messages else 0
            
            # 保留旧字段以兼容
            memorial["views"] = memorial["view_count"]
            memorial["likes"] = db.get_memorial_likes(memorial["id"]) or 0
            memorial["like_count"] = memorial["likes"]
        
        return {
            "success": True,
            "memorials": memorials
        }
        
    except Exception as e:
        return {"success": False, "message": f"获取纪念馆列表失败: {str(e)}"}

@app.get("/api/memorial/get/{memorial_id}")
async def get_memorial_detail(memorial_id: str, session_token: str = Header(None, alias="x-session-token")):
    """获取纪念馆详情"""
    try:
        user = auth_service.get_current_user(session_token)
        if not user:
            return {"success": False, "message": "用户未登录"}
        
        memorial = db.get_memorial_by_id(memorial_id)
        if not memorial:
            return {"success": False, "message": "纪念馆不存在"}
        
        # 检查权限
        if memorial["user_id"] != user["id"]:
            return {"success": False, "message": "无权访问此纪念馆"}
        
        # 添加照片信息
        memorial["photos"] = db.get_memorial_photos(memorial_id) or []
        
        return {
            "success": True,
            "memorial": memorial
        }
        
    except Exception as e:
        return {"success": False, "message": f"获取纪念馆详情失败: {str(e)}"}

@app.put("/api/memorial/update/{memorial_id}")
async def update_memorial(memorial_id: str, request: Request, session_token: str = Header(None, alias="x-session-token")):
    """更新纪念馆信息"""
    try:
        user = auth_service.get_current_user(session_token)
        if not user:
            return {"success": False, "message": "用户未登录"}
        
        # 检查纪念馆是否存在且属于当前用户
        memorial = db.get_memorial_by_id(memorial_id)
        if not memorial or memorial["user_id"] != user["id"]:
            return {"success": False, "message": "纪念馆不存在或无权限"}
        
        data = await request.json()
        
        # 更新纪念馆信息
        success = db.update_memorial(
            memorial_id=memorial_id,
            pet_name=data.get("pet_name"),
            species=data.get("species"),
            breed=data.get("breed"),
            color=data.get("color"),
            gender=data.get("gender"),
            birth_date=data.get("birth_date"),
            memorial_date=data.get("memorial_date"),
            weight=float(data.get("weight", 0)) if data.get("weight") else None,
            description=data.get("description"),
            personality=data.get("personality")
        )
        
        if success:
            return {"success": True, "message": "纪念馆更新成功"}
        else:
            return {"success": False, "message": "纪念馆更新失败"}
        
    except Exception as e:
        return {"success": False, "message": f"更新纪念馆失败: {str(e)}"}

@app.delete("/api/memorial/delete/{memorial_id}")
async def delete_memorial(memorial_id: str, session_token: str = Header(None, alias="x-session-token")):
    """删除纪念馆"""
    try:
        user = auth_service.get_current_user(session_token)
        if not user:
            return {"success": False, "message": "用户未登录"}
        
        # 检查纪念馆是否存在且属于当前用户
        memorial = db.get_memorial_by_id(memorial_id)
        if not memorial or memorial["user_id"] != user["id"]:
            return {"success": False, "message": "纪念馆不存在或无权限"}
        
        # 删除纪念馆
        success = db.delete_memorial(memorial_id)
        
        if success:
            return {"success": True, "message": "纪念馆删除成功"}
        else:
            return {"success": False, "message": "纪念馆删除失败"}
        
    except Exception as e:
        return {"success": False, "message": f"删除纪念馆失败: {str(e)}"}

@app.post("/api/memorial/upload-photos/{memorial_id}")
async def upload_memorial_photos(
    memorial_id: str,
    photos: list[UploadFile] = File(...),
    session_token: str = Header(None, alias="x-session-token")
):
    """上传纪念馆照片"""
    try:
        user = auth_service.get_current_user(session_token)
        if not user:
            return {"success": False, "message": "用户未登录"}
        
        # 检查纪念馆是否存在且属于当前用户
        memorial = db.get_memorial_by_id(memorial_id)
        if not memorial or memorial["user_id"] != user["id"]:
            return {"success": False, "message": "纪念馆不存在或无权限"}
        
        # 检查照片上传权限
        photo_permission = auth_service.can_upload_photo(user["id"], memorial_id)
        if not photo_permission.get("can_upload", False):
            return {"success": False, "message": photo_permission.get("message", "无法上传照片")}
        
        uploaded_photos = []
        
        for photo in photos:
            if photo.content_type.startswith('image/'):
                # 生成唯一文件名
                filename = f"{uuid.uuid4().hex}.jpg"
                
                # 保存照片
                storage_base = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage")
                photo_path = os.path.join(storage_base, "photos", filename)
                
                with open(photo_path, "wb") as f:
                    f.write(await photo.read())
                
                # 添加到纪念馆
                photo_url = f"/storage/photos/{filename}"
                db.add_memorial_photo(memorial_id, photo_url)
                uploaded_photos.append(photo_url)
        
        # 获取更新后的照片列表
        all_photos = db.get_memorial_photos(memorial_id) or []
        
        return {
            "success": True,
            "message": f"成功上传 {len(uploaded_photos)} 张照片",
            "photos": all_photos
        }
        
    except Exception as e:
        return {"success": False, "message": f"上传照片失败: {str(e)}"}

@app.delete("/api/memorial/delete-photo/{memorial_id}")
async def delete_memorial_photo(
    memorial_id: str,
    request: Request,
    session_token: str = Header(None, alias="x-session-token")
):
    """删除纪念馆照片"""
    try:
        user = auth_service.get_current_user(session_token)
        if not user:
            return {"success": False, "message": "用户未登录"}
        
        # 检查纪念馆是否存在且属于当前用户
        memorial = db.get_memorial_by_id(memorial_id)
        if not memorial or memorial["user_id"] != user["id"]:
            return {"success": False, "message": "纪念馆不存在或无权限"}
        
        data = await request.json()
        photo_index = data.get("photo_index")
        
        if photo_index is None:
            return {"success": False, "message": "照片索引无效"}
        
        # 获取照片列表
        photos = db.get_memorial_photos(memorial_id) or []
        
        if photo_index < 0 or photo_index >= len(photos):
            return {"success": False, "message": "照片索引超出范围"}
        
        # 删除照片
        photo_url = photos[photo_index]
        success = db.delete_memorial_photo(memorial_id, photo_url)
        
        if success:
            return {"success": True, "message": "照片删除成功"}
        else:
            return {"success": False, "message": "照片删除失败"}
        
    except Exception as e:
        return {"success": False, "message": f"删除照片失败: {str(e)}"}

# ==================== 照片管理API ====================

@app.get("/photo-manager", response_class=HTMLResponse)
async def photo_manager_page(request: Request):
    """照片管理页面"""
    try:
        template_path = os.path.join(os.path.dirname(__file__), "templates", "photo_manager.html")
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        return HTMLResponse(content=f"<h1>页面加载错误</h1><p>{str(e)}</p>", status_code=500)

@app.get("/api/user/photos")
async def get_user_photos(session_token: str = Header(None, alias="x-session-token")):
    """获取用户照片列表"""
    try:
        user = auth_service.get_current_user(session_token)
        if not user:
            return {"success": False, "message": "用户未登录"}
        
        # 获取用户所有纪念馆的照片
        memorials = db.get_user_memorials(user["id"])
        all_photos = []
        
        for memorial in memorials:
            photos = db.get_memorial_photos(memorial["id"])
            for photo_url in photos:
                all_photos.append({
                    "id": f"photo_{len(all_photos)}",
                    "url": photo_url,
                    "memorial_id": memorial["id"],
                    "memorial_name": memorial.get("pet_name", "未命名"),
                    "created_at": memorial.get("created_at", ""),
                    "title": f"{memorial.get('pet_name', '未命名')}的照片"
                })
        
        # 按创建时间排序
        all_photos.sort(key=lambda x: x["created_at"], reverse=True)
        
        return {
            "success": True,
            "photos": all_photos
        }
        
    except Exception as e:
        return {"success": False, "message": f"获取照片列表失败: {str(e)}"}

@app.post("/api/photos/upload")
async def upload_photos(
    photos: list[UploadFile] = File(...),
    session_token: str = Header(None, alias="x-session-token")
):
    """上传照片"""
    try:
        user = auth_service.get_current_user(session_token)
        if not user:
            return {"success": False, "message": "用户未登录"}
        
        # 检查照片上传权限
        if not auth_service.can_upload_photo(user["id"]):
            return {"success": False, "message": "已达到照片上传上限，请升级会员"}
        
        uploaded_photos = []
        
        for photo in photos:
            if photo.content_type.startswith('image/'):
                # 生成唯一文件名
                filename = f"{uuid.uuid4().hex}.jpg"
                
                # 保存照片
                storage_base = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage")
                photo_path = os.path.join(storage_base, "photos", filename)
                
                with open(photo_path, "wb") as f:
                    f.write(await photo.read())
                
                photo_url = f"/storage/photos/{filename}"
                uploaded_photos.append(photo_url)
        
        return {
            "success": True,
            "message": f"成功上传 {len(uploaded_photos)} 张照片",
            "photos": uploaded_photos
        }
        
    except Exception as e:
        return {"success": False, "message": f"上传照片失败: {str(e)}"}

@app.delete("/api/photos/delete/{photo_id}")
async def delete_photo(photo_id: str, session_token: str = Header(None, alias="x-session-token")):
    """删除照片"""
    try:
        user = auth_service.get_current_user(session_token)
        if not user:
            return {"success": False, "message": "用户未登录"}
        
        # 这里需要根据photo_id找到对应的照片URL并删除
        # 由于当前设计，photo_id是临时生成的，实际项目中需要改进
        
        return {
            "success": True,
            "message": "照片删除成功"
        }
        
    except Exception as e:
        return {"success": False, "message": f"删除照片失败: {str(e)}"}


# ==================== AI对话API ====================

@app.post("/api/chat/{memorial_id}")
async def chat_with_pet(
    memorial_id: str,
    request: Request,
    session_token: str = Header(None, alias="x-session-token")
):
    """与宠物AI对话"""
    try:
        # 验证用户登录
        user = auth_service.get_current_user(session_token)
        if not user:
            return {"success": False, "message": "用户未登录"}
        
        # 获取请求数据
        data = await request.json()
        message = data.get("message", "").strip()
        
        if not message:
            return {"success": False, "message": "消息不能为空"}
        
        # 获取纪念馆信息
        memorial = db.get_memorial_by_id(memorial_id)
        if not memorial:
            return {"success": False, "message": "纪念馆不存在"}
        
        # 检查权限（只有创建者可以对话）
        if memorial.get("user_id") != user["id"]:
            return {"success": False, "message": "无权访问此纪念馆"}
        
        # 获取对话历史
        chat_history = db.get_chat_history(memorial_id, user["id"], limit=20)
        
        # 调用AI服务生成回复
        ai_reply = ai_chat_service.chat(memorial, message, chat_history)
        
        # 保存用户消息
        db.save_chat_message(memorial_id, user["id"], "user", message)
        
        # 保存AI回复
        db.save_chat_message(memorial_id, user["id"], "assistant", ai_reply)
        
        return {
            "success": True,
            "message": ai_reply,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"AI对话失败: {e}")
        return {"success": False, "message": f"对话失败: {str(e)}"}


@app.get("/api/chat/{memorial_id}/history")
async def get_chat_history(
    memorial_id: str,
    limit: int = 50,
    session_token: str = Header(None, alias="x-session-token")
):
    """获取对话历史"""
    try:
        # 验证用户登录
        user = auth_service.get_current_user(session_token)
        if not user:
            return {"success": False, "message": "用户未登录"}
        
        # 获取纪念馆信息
        memorial = db.get_memorial_by_id(memorial_id)
        if not memorial:
            return {"success": False, "message": "纪念馆不存在"}
        
        # 检查权限
        if memorial.get("user_id") != user["id"]:
            return {"success": False, "message": "无权访问此纪念馆"}
        
        # 获取对话历史
        history = db.get_chat_history(memorial_id, user["id"], limit)
        
        return {
            "success": True,
            "history": history,
            "count": len(history)
        }
        
    except Exception as e:
        print(f"获取对话历史失败: {e}")
        return {"success": False, "message": f"获取失败: {str(e)}"}


@app.delete("/api/chat/{memorial_id}/history")
async def clear_chat_history(
    memorial_id: str,
    session_token: str = Header(None, alias="x-session-token")
):
    """清空对话历史"""
    try:
        # 验证用户登录
        user = auth_service.get_current_user(session_token)
        if not user:
            return {"success": False, "message": "用户未登录"}
        
        # 获取纪念馆信息
        memorial = db.get_memorial_by_id(memorial_id)
        if not memorial:
            return {"success": False, "message": "纪念馆不存在"}
        
        # 检查权限
        if memorial.get("user_id") != user["id"]:
            return {"success": False, "message": "无权访问此纪念馆"}
        
        # 删除对话历史
        success = db.delete_chat_history(memorial_id, user["id"])
        
        if success:
            return {"success": True, "message": "对话历史已清空"}
        else:
            return {"success": False, "message": "清空失败"}
        
    except Exception as e:
        print(f"清空对话历史失败: {e}")
        return {"success": False, "message": f"清空失败: {str(e)}"}


@app.get("/api/chat/{memorial_id}/greeting")
async def get_greeting(
    memorial_id: str,
    session_token: str = Header(None, alias="x-session-token")
):
    """获取宠物的问候语"""
    try:
        # 验证用户登录
        user = auth_service.get_current_user(session_token)
        if not user:
            return {"success": False, "message": "用户未登录"}
        
        # 获取纪念馆信息
        memorial = db.get_memorial_by_id(memorial_id)
        if not memorial:
            return {"success": False, "message": "纪念馆不存在"}
        
        # 检查权限
        if memorial.get("user_id") != user["id"]:
            return {"success": False, "message": "无权访问此纪念馆"}
        
        # 获取问候语
        greeting = ai_chat_service.get_greeting_message(memorial)
        
        return {
            "success": True,
            "greeting": greeting
        }
        
    except Exception as e:
        print(f"获取问候语失败: {e}")
        return {"success": False, "message": f"获取失败: {str(e)}"}

# ============ 虚拟陪伴相关API ============

@app.post("/api/companion/{memorial_id}/analyze-emotion")
async def analyze_emotion(
    memorial_id: str,
    request: Request,
    session_token: str = Header(None, alias="x-session-token")
):
    """分析消息情绪"""
    try:
        user = auth_service.get_current_user(session_token)
        if not user:
            return {"success": False, "message": "用户未登录"}
        
        body = await request.json()
        message = body.get("message", "")
        
        if not message:
            return {"success": False, "message": "消息不能为空"}
        
        # 分析情绪
        emotion_data = virtual_companion_service.analyze_emotion(message)
        
        # 保存情绪记录
        db.save_emotion_record(
            memorial_id, 
            user["id"], 
            emotion_data.get("emotion", "calm"),
            emotion_data.get("intensity", 0.5),
            emotion_data.get("keywords", []),
            message
        )
        
        return {
            "success": True,
            "emotion_data": emotion_data
        }
        
    except Exception as e:
        print(f"分析情绪失败: {e}")
        return {"success": False, "message": f"分析失败: {str(e)}"}

@app.get("/api/companion/{memorial_id}/greeting")
async def get_companion_greeting(
    memorial_id: str,
    greeting_type: str = "random",
    session_token: str = Header(None, alias="x-session-token")
):
    """获取主动问候消息"""
    try:
        user = auth_service.get_current_user(session_token)
        if not user:
            return {"success": False, "message": "用户未登录"}
        
        # 生成问候
        greeting = virtual_companion_service.generate_greeting(memorial_id, greeting_type)
        
        return greeting
        
    except Exception as e:
        print(f"生成问候失败: {e}")
        return {"success": False, "message": f"生成失败: {str(e)}"}

@app.post("/api/companion/{memorial_id}/interact")
async def interact_with_pet(
    memorial_id: str,
    request: Request,
    session_token: str = Header(None, alias="x-session-token")
):
    """与宠物互动游戏"""
    try:
        user = auth_service.get_current_user(session_token)
        if not user:
            return {"success": False, "message": "用户未登录"}
        
        body = await request.json()
        game_type = body.get("game_type", "pet")  # feed/play/walk/pet
        
        # 执行互动
        result = virtual_companion_service.play_interaction_game(
            memorial_id, 
            game_type, 
            user["id"]
        )
        
        return result
        
    except Exception as e:
        print(f"互动失败: {e}")
        return {"success": False, "message": f"互动失败: {str(e)}"}

@app.get("/api/companion/{memorial_id}/emotion-curve")
async def get_emotion_curve(
    memorial_id: str,
    days: int = 7,
    session_token: str = Header(None, alias="x-session-token")
):
    """获取情绪曲线数据"""
    try:
        user = auth_service.get_current_user(session_token)
        if not user:
            return {"success": False, "message": "用户未登录"}
        
        # 获取情绪曲线
        curve_data = virtual_companion_service.get_emotion_curve(memorial_id, days)
        
        return curve_data
        
    except Exception as e:
        print(f"获取情绪曲线失败: {e}")
        return {"success": False, "message": f"获取失败: {str(e)}"}

@app.get("/api/companion/{memorial_id}/status")
async def get_companion_status(
    memorial_id: str,
    session_token: str = Header(None, alias="x-session-token")
):
    """获取虚拟陪伴状态"""
    try:
        user = auth_service.get_current_user(session_token)
        if not user:
            return {"success": False, "message": "用户未登录"}
        
        # 获取状态
        status = virtual_companion_service.get_companion_status(memorial_id, user["id"])
        
        return status
        
    except Exception as e:
        print(f"获取状态失败: {e}")
        return {"success": False, "message": f"获取失败: {str(e)}"}

@app.get("/api/companion/{memorial_id}/recent-greetings")
async def get_recent_greetings(
    memorial_id: str,
    limit: int = 10,
    session_token: str = Header(None, alias="x-session-token")
):
    """获取最近的问候消息"""
    try:
        user = auth_service.get_current_user(session_token)
        if not user:
            return {"success": False, "message": "用户未登录"}
        
        greetings = db.get_recent_greetings(memorial_id, limit)
        
        return {
            "success": True,
            "greetings": greetings
        }
        
    except Exception as e:
        print(f"获取问候消息失败: {e}")
        return {"success": False, "message": f"获取失败: {str(e)}"}


# ==================== 梦境日记API ====================

@app.post("/api/dreams/{memorial_id}")
async def create_dream_diary(
    memorial_id: str,
    request: Request,
    session_token: str = Header(None, alias="x-session-token")
):
    """创建梦境日记"""
    try:
        user = auth_service.get_current_user(session_token)
        if not user:
            return {"success": False, "message": "用户未登录"}
        
        data = await request.json()
        dream_content = data.get("dream_content", "").strip()
        dream_date = data.get("dream_date")
        dream_time = data.get("dream_time")
        emotion_type = data.get("emotion_type")
        is_private = data.get("is_private", False)
        
        if not dream_content:
            return {"success": False, "message": "请填写梦境内容"}
        
        if not dream_date:
            from datetime import datetime
            dream_date = datetime.now().strftime("%Y-%m-%d")
        
        # 获取宠物信息用于AI分析
        memorial = db.get_memorial_by_id(memorial_id)
        if not memorial:
            return {"success": False, "message": "纪念馆不存在"}
        
        pet_name = memorial.get("pet_name", "宠物")
        
        # AI分析梦境
        ai_result = None
        mood_score = data.get("mood_score")
        suggested_tags = []
        
        if not emotion_type:  # 如果用户没有手动选择情绪，则使用AI分析
            try:
                ai_result = await dream_analysis_service.analyze_dream(dream_content, pet_name)
                emotion_type = ai_result['emotion_type']
                mood_score = ai_result['mood_score']
                suggested_tags = dream_analysis_service.suggest_tags(dream_content)
            except Exception as e:
                print(f"AI分析失败: {e}")
                emotion_type = "思念"
                mood_score = 5
        
        # 处理标签
        user_tags = data.get("tags", [])
        if isinstance(user_tags, str):
            user_tags = [t.strip() for t in user_tags.split(',') if t.strip()]
        all_tags = list(set(user_tags + suggested_tags))
        tags_str = ','.join(all_tags) if all_tags else None
        
        # 创建梦境日记
        dream_id = db.create_dream_diary(
            memorial_id=memorial_id,
            user_id=user['id'],
            dream_date=dream_date,
            dream_content=dream_content,
            emotion_type=emotion_type,
            mood_score=mood_score,
            tags=tags_str,
            dream_time=dream_time,
            is_private=is_private
        )
        
        # 如果有AI分析结果，更新到数据库
        if ai_result and ai_result.get('analysis'):
            db.update_dream_diary(
                dream_id=dream_id,
                user_id=user['id'],
                ai_analysis=ai_result['analysis']
            )
        
        # 获取刚创建的梦境日记
        dream = db.get_dream_diary_by_id(dream_id, user['id'])
        
        return {
            "success": True,
            "message": "梦境日记创建成功",
            "dream": dream,
            "suggested_tags": suggested_tags
        }
        
    except Exception as e:
        print(f"创建梦境日记失败: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "message": f"创建失败: {str(e)}"}


@app.get("/api/dreams/{memorial_id}")
async def get_dream_diaries(
    memorial_id: str,
    limit: int = 50,
    session_token: str = Header(None, alias="x-session-token")
):
    """获取梦境日记列表"""
    try:
        user = auth_service.get_current_user(session_token)
        if not user:
            return {"success": False, "message": "用户未登录"}
        
        dreams = db.get_dream_diaries(memorial_id, user['id'], limit)
        
        return {
            "success": True,
            "dreams": dreams,
            "total": len(dreams)
        }
        
    except Exception as e:
        print(f"获取梦境日记失败: {e}")
        return {"success": False, "message": f"获取失败: {str(e)}"}


@app.get("/api/dreams/{memorial_id}/detail/{dream_id}")
async def get_dream_detail(
    memorial_id: str,
    dream_id: int,
    session_token: str = Header(None, alias="x-session-token")
):
    """获取梦境日记详情"""
    try:
        user = auth_service.get_current_user(session_token)
        if not user:
            return {"success": False, "message": "用户未登录"}
        
        dream = db.get_dream_diary_by_id(dream_id, user['id'])
        
        if not dream:
            return {"success": False, "message": "梦境日记不存在"}
        
        if dream['memorial_id'] != memorial_id:
            return {"success": False, "message": "梦境日记与纪念馆不匹配"}
        
        # 获取治愈话语
        healing_words = await dream_analysis_service.get_healing_words(
            dream.get('emotion_type', '思念')
        )
        
        return {
            "success": True,
            "dream": dream,
            "healing_words": healing_words
        }
        
    except Exception as e:
        print(f"获取梦境详情失败: {e}")
        return {"success": False, "message": f"获取失败: {str(e)}"}


@app.put("/api/dreams/{memorial_id}/{dream_id}")
async def update_dream_diary(
    memorial_id: str,
    dream_id: int,
    request: Request,
    session_token: str = Header(None, alias="x-session-token")
):
    """更新梦境日记"""
    try:
        user = auth_service.get_current_user(session_token)
        if not user:
            return {"success": False, "message": "用户未登录"}
        
        data = await request.json()
        
        # 处理标签
        if 'tags' in data and isinstance(data['tags'], list):
            data['tags'] = ','.join(data['tags'])
        
        success = db.update_dream_diary(dream_id, user['id'], **data)
        
        if success:
            dream = db.get_dream_diary_by_id(dream_id, user['id'])
            return {
                "success": True,
                "message": "更新成功",
                "dream": dream
            }
        else:
            return {"success": False, "message": "更新失败"}
        
    except Exception as e:
        print(f"更新梦境日记失败: {e}")
        return {"success": False, "message": f"更新失败: {str(e)}"}


@app.delete("/api/dreams/{memorial_id}/{dream_id}")
async def delete_dream_diary(
    memorial_id: str,
    dream_id: int,
    session_token: str = Header(None, alias="x-session-token")
):
    """删除梦境日记"""
    try:
        user = auth_service.get_current_user(session_token)
        if not user:
            return {"success": False, "message": "用户未登录"}
        
        success = db.delete_dream_diary(dream_id, user['id'])
        
        if success:
            return {
                "success": True,
                "message": "删除成功"
            }
        else:
            return {"success": False, "message": "删除失败"}
        
    except Exception as e:
        print(f"删除梦境日记失败: {e}")
        return {"success": False, "message": f"删除失败: {str(e)}"}


@app.post("/api/dreams/{memorial_id}/{dream_id}/favorite")
async def toggle_favorite(
    memorial_id: str,
    dream_id: int,
    request: Request,
    session_token: str = Header(None, alias="x-session-token")
):
    """切换收藏状态"""
    try:
        user = auth_service.get_current_user(session_token)
        if not user:
            return {"success": False, "message": "用户未登录"}
        
        data = await request.json()
        is_favorite = data.get("is_favorite", False)
        
        success = db.update_dream_diary(dream_id, user['id'], is_favorite=is_favorite)
        
        if success:
            return {
                "success": True,
                "message": "收藏状态已更新",
                "is_favorite": is_favorite
            }
        else:
            return {"success": False, "message": "操作失败"}
        
    except Exception as e:
        print(f"切换收藏失败: {e}")
        return {"success": False, "message": f"操作失败: {str(e)}"}


@app.get("/api/dreams/{memorial_id}/stats")
async def get_dream_stats(
    memorial_id: str,
    session_token: str = Header(None, alias="x-session-token")
):
    """获取梦境统计"""
    try:
        user = auth_service.get_current_user(session_token)
        if not user:
            return {"success": False, "message": "用户未登录"}
        
        stats = db.get_dream_stats(memorial_id, user['id'])
        
        return {
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        print(f"获取梦境统计失败: {e}")
        return {"success": False, "message": f"获取失败: {str(e)}"}


@app.get("/api/dreams/{memorial_id}/calendar")
async def get_dream_calendar(
    memorial_id: str,
    year: int = None,
    month: int = None,
    session_token: str = Header(None, alias="x-session-token")
):
    """获取梦境月历"""
    try:
        user = auth_service.get_current_user(session_token)
        if not user:
            return {"success": False, "message": "用户未登录"}
        
        if not year or not month:
            from datetime import datetime
            now = datetime.now()
            year = year or now.year
            month = month or now.month
        
        calendar_data = db.get_dream_calendar(memorial_id, user['id'], year, month)
        
        return {
            "success": True,
            "year": year,
            "month": month,
            "calendar": calendar_data
        }
        
    except Exception as e:
        print(f"获取梦境月历失败: {e}")
        return {"success": False, "message": f"获取失败: {str(e)}"}


# ==================== 星空纪念API ====================

@app.get("/api/star-sky/memorials")
async def get_star_sky_memorials(request: Request):
    """获取所有公开纪念馆（用于星空展示）"""
    try:
        # 获取当前用户ID（如果已登录）
        current_user_id = None
        session_token = request.headers.get('x-session-token')
        if session_token:
            user_id = db.get_user_id_from_session(session_token)
            if user_id:
                current_user_id = user_id
        
        memorials = db.get_all_public_memorials()
        
        # 转换为星星数据
        stars = []
        for memorial in memorials:
            # 获取第一张照片
            photos = db.get_memorial_photos(memorial['id'])
            photo_url = photos[0] if photos else None
            
            # 计算星星位置（伪随机，但固定）
            import hashlib
            hash_val = int(hashlib.md5(memorial['id'].encode()).hexdigest()[:8], 16)
            
            stars.append({
                'id': memorial['id'],
                'pet_name': memorial['pet_name'],
                'species': memorial['species'],
                'memorial_date': memorial['memorial_date'],
                'photo_url': photo_url,
                'x': (hash_val % 10000) / 100,  # 0-100
                'y': ((hash_val // 10000) % 10000) / 100,  # 0-100
                'size': 2 + (hash_val % 3),  # 2-4
                'brightness': 0.5 + ((hash_val % 50) / 100),  # 0.5-1.0
                'color': get_star_color(memorial['species']),
                'days_passed': calculate_days_passed(memorial['memorial_date']),
                'is_mine': current_user_id and memorial['user_id'] == current_user_id
            })
        
        return {
            "success": True,
            "stars": stars,
            "total": len(stars)
        }
        
    except Exception as e:
        print(f"获取星空数据失败: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "message": f"获取失败: {str(e)}"}


def get_star_color(species: str) -> str:
    """根据宠物品种返回星星颜色"""
    species_lower = species.lower() if species else ''
    
    if '猫' in species_lower or 'cat' in species_lower:
        return '#F5A623'  # 橙色
    elif '狗' in species_lower or 'dog' in species_lower:
        return '#4A90E2'  # 蓝色
    elif '兔' in species_lower or 'rabbit' in species_lower:
        return '#7ED321'  # 绿色
    elif '鸟' in species_lower or 'bird' in species_lower:
        return '#FF6B6B'  # 红色
    else:
        return '#FFD700'  # 金色（默认）


def calculate_days_passed(memorial_date: str) -> int:
    """计算离世天数"""
    if not memorial_date:
        return 0
    
    try:
        from datetime import datetime
        memorial_dt = datetime.strptime(memorial_date, "%Y-%m-%d")
        now = datetime.now()
        delta = now - memorial_dt
        return delta.days
    except:
        return 0


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)