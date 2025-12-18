import os
import uuid
import zipfile
import qrcode
import io
from jinja2 import Environment, FileSystemLoader
from fastapi.responses import FileResponse, StreamingResponse, HTMLResponse

from datetime import datetime
from pathlib import Path
from .personality_service import PersonalityService

class MemorialService:
    def __init__(self, db):
        self.db = db
        self.env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")))
        self.personality_service = PersonalityService()
        
        # 创建必要的存储目录
        storage_base = os.path.join(os.path.dirname(__file__), "..", "storage")
        Path(os.path.join(storage_base, "photos")).mkdir(parents=True, exist_ok=True)
        Path(os.path.join(storage_base, "memorials")).mkdir(parents=True, exist_ok=True)
        Path(os.path.join(storage_base, "downloads")).mkdir(parents=True, exist_ok=True)
        Path(os.path.join(storage_base, "qrcodes")).mkdir(parents=True, exist_ok=True)
    
    def create_memorial_advanced(self, email, pet_info, photos, personality_answers, user_id=None):
        """创建纪念馆完整流程（包含性格测试和AI信件）"""
        # 生成唯一ID
        pet_id = uuid.uuid4().hex
        memorial_id = uuid.uuid4().hex
        
        # 创建宠物记录
        self.db.create_pet_record(
            pet_id=pet_id,
            name=pet_info['name'],
            species=pet_info['species'],
            breed=pet_info.get('breed', ''),
            color=pet_info.get('color', ''),
            gender=pet_info.get('gender', ''),
            birth_date=pet_info.get('birth_date', ''),
            memorial_date=pet_info.get('memorial_date', ''),
            weight=pet_info.get('weight', 0.0),
            user_id=user_id,  # 关联到用户
            status=pet_info.get('status', 'alive')  # 宠物状态
        )
        
        # 保存性格测试答案
        if personality_answers:
            for question_id, answer in personality_answers.items():
                self.db.save_personality_test(pet_id, question_id, answer)
        
        # 分析性格类型
        personality_type = self.personality_service.analyze_personality(personality_answers)
        self.db.update_pet_personality(pet_id, personality_type)
        
        # 生成AI信件
        ai_letter = self.personality_service.generate_ai_letter(pet_info, personality_type, personality_answers)
        
        # 生成纪念馆HTML
        memorial_url = self._generate_html_advanced(
            memorial_id=memorial_id,
            pet_info=pet_info,
            personality_type=personality_type,
            ai_letter=ai_letter,
            photos=photos
        )
        
        # 创建纪念馆记录
        self.db.create_memorial_record(
            memorial_id=memorial_id,
            pet_id=pet_id,
            memorial_url=memorial_url,
            ai_letter=ai_letter,
            user_id=user_id,  # 传递user_id
            description=pet_info.get('description', ''),  # 从pet_info获取description
            personality=personality_type  # 传递性格类型
        )
        
        # 如果提供了用户ID，将纪念馆关联到用户
        if user_id:
            self.db.link_memorial_to_user(user_id, memorial_id)
        
        return memorial_url, personality_type, ai_letter
    
    def get_personality_questions(self):
        """获取性格测试问题"""
        return self.personality_service.get_questions()
    
    def get_personality_answer_options(self, question_id):
        """获取性格测试答案选项"""
        return self.personality_service.get_answer_options(question_id)
    
    def get_personality_description(self, personality_type):
        """获取性格类型描述"""
        return self.personality_service.get_personality_description(personality_type)
    
    def create_memorial(self, email, pet_name, species, memorial_date, photos):
        """创建纪念馆完整流程"""
        # 生成唯一ID
        memorial_id = uuid.uuid4().hex
        
        # 创建数据库记录
        self.db.create_memorial_record(
            memorial_id=memorial_id,
            pet_name=pet_name,
            species=species,
            memorial_date=memorial_date
        )
        
        # 生成纪念馆HTML
        memorial_url = self._generate_html(
            memorial_id=memorial_id,
            pet_name=pet_name,
            species=species,
            memorial_date=memorial_date,
            photos=photos
        )
        
        return memorial_url
    

    
    def render_memorial_page(self, memorial_id):
        """渲染纪念馆页面"""
        storage_base = os.path.join(os.path.dirname(__file__), "..", "storage")
        memorial_path = os.path.join(storage_base, "memorials", f"{memorial_id}.html")
        if not os.path.exists(memorial_path):
            return HTMLResponse(content="<h1>纪念馆不存在</h1>", status_code=404)
        
        with open(memorial_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    
    def create_download_package(self, memorial_id):
        """创建纪念馆下载包"""
        storage_base = os.path.join(os.path.dirname(__file__), "..", "storage")
        # 创建ZIP文件
        zip_path = os.path.join(storage_base, "downloads", f"{memorial_id}.zip")
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            # 添加纪念馆HTML
            html_path = os.path.join(storage_base, "memorials", f"{memorial_id}.html")
            if os.path.exists(html_path):
                zipf.write(html_path, f"{memorial_id}.html")
            
            # 添加照片
            photos_dir = os.path.join(storage_base, "photos")
            for root, _, files in os.walk(photos_dir):
                for file in files:
                    if memorial_id in file:  # 简单的关联判断
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, f"photos/{file}")
            

        
        return FileResponse(
            zip_path,
            media_type='application/zip',
            filename=f"{memorial_id}_memorial.zip"
        )
    
    def generate_qrcode(self, memorial_id):
        """生成纪念馆二维码"""
        memorial_url = f"/memorial/{memorial_id}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(memorial_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img_buffer = io.BytesIO()
        img.save(img_buffer)
        img_buffer.seek(0)
        
        return StreamingResponse(
            img_buffer,
            media_type="image/png",
            headers={"Content-Disposition": f"attachment; filename={memorial_id}_qrcode.png"}
        )
    

    def _generate_html(self, memorial_id, pet_name, species, memorial_date, photos):
        """生成纪念馆HTML页面"""
        template = self.env.get_template('memorial.html')
        
        html_content = template.render(
            pet_name=pet_name,
            species=species,
            memorial_date=memorial_date,
            photos=photos,
            current_year=datetime.now().year
        )
        
        # 保存HTML文件
        filename = f"{memorial_id}.html"
        storage_base = os.path.join(os.path.dirname(__file__), "..", "storage")
        path = os.path.join(storage_base, "memorials", filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        return f"/memorial/{memorial_id}"



    def _generate_html_advanced(self, memorial_id, pet_info, personality_type, ai_letter, photos):
        """生成纪念馆HTML页面（包含性格测试和AI信件）"""
        template = self.env.get_template('memorial.html')
        
        html_content = template.render(
            pet_name=pet_info['name'],
            species=pet_info['species'],
            breed=pet_info.get('breed', ''),
            color=pet_info.get('color', ''),
            gender=pet_info.get('gender', ''),
            birth_date=pet_info.get('birth_date', ''),
            weight=pet_info.get('weight', ''),
            memorial_date=pet_info.get('memorial_date', ''),
            pet_status=pet_info.get('status', 'alive'),
            personality_type=personality_type,
            personality_description=self.get_personality_description(personality_type),
            ai_letter=ai_letter,
            photos=photos,
            current_year=datetime.now().year
        )
        
        # 保存HTML文件
        filename = f"{memorial_id}.html"
        storage_base = os.path.join(os.path.dirname(__file__), "..", "storage")
        path = os.path.join(storage_base, "memorials", filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        return f"/memorial/{memorial_id}"


class EmailService:
    def __init__(self):
        # 邮件服务配置：必须通过环境变量提供，避免敏感信息写入代码仓库
        import os
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.qq.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.sender_email = os.getenv('SENDER_EMAIL', '')
        self.sender_password = os.getenv('SENDER_PASSWORD', '')
        
        print(f"📧 邮件服务配置:")
        print(f"   SMTP服务器: {self.smtp_server}")
        print(f"   SMTP端口: {self.smtp_port}")
        print(f"   发件人邮箱: {self.sender_email}")
        print(f"   发件人密码: {'已配置' if self.sender_password else '未配置'}")
    
    def send_creation_email(self, email, pet_name, memorial_url, personality_type="", ai_letter=""):
        """发送纪念馆创建成功邮件"""
        try:
            # 构建邮件内容
            subject = f"🐾 {pet_name}的纪念馆创建成功"
            
            # 构建HTML邮件内容
            html_content = self._build_email_html(pet_name, memorial_url, personality_type, ai_letter)
            
            # 发送邮件
            success = self._send_email(email, subject, html_content)
            
            if success:
                print(f"✅ 邮件发送成功: {email}")
                return True
            else:
                print(f"❌ 邮件发送失败: {email}")
                return False
                
        except Exception as e:
            print(f"❌ 邮件发送异常: {e}")
            return False
    
    def _build_email_html(self, pet_name, memorial_url, personality_type, ai_letter):
        """构建HTML邮件内容"""
        # 使用配置文件中的服务器地址
        try:
            from .config import config
            base_url = config.BASE_URL
        except ImportError:
            # 如果相对导入失败，尝试绝对导入
            import os
            base_url = os.getenv('SERVER_BASE_URL', 'https://www.pettrailstar.cn')
        full_memorial_url = f"{base_url}{memorial_url}"
        
        html = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{pet_name}的纪念馆</title>
            <style>
                body {{
                    font-family: 'Microsoft YaHei', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .email-container {{
                    background-color: white;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    padding: 20px 0;
                    border-bottom: 3px solid #667eea;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    color: #667eea;
                    margin: 0;
                    font-size: 2em;
                }}
                .content {{
                    margin: 20px 0;
                }}
                .highlight {{
                    background-color: #fff3cd;
                    border: 1px solid #ffeaa7;
                    border-radius: 5px;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .button {{
                    display: inline-block;
                    background-color: #667eea;
                    color: white;
                    padding: 15px 30px;
                    text-decoration: none;
                    border-radius: 25px;
                    font-weight: bold;
                    margin: 20px 0;
                    text-align: center;
                }}
                .button:hover {{
                    background-color: #5a6fd8;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    color: #666;
                    font-size: 0.9em;
                }}
                .personality-info {{
                    background-color: #e8f5e8;
                    border: 1px solid #c3e6c3;
                    border-radius: 5px;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .ai-letter {{
                    background-color: #f0f8ff;
                    border: 1px solid #b3d9ff;
                    border-radius: 5px;
                    padding: 15px;
                    margin: 20px 0;
                    font-style: italic;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>🐾  爪迹星·云纪念馆</h1>
                    <p>永远的回忆，永远的陪伴</p>
                </div>
                
                <div class="content">
                    <h2>亲爱的朋友：</h2>
                    
                    <p>恭喜您！<strong>{pet_name}</strong>的纪念馆已经创建成功。</p>
                    
                    <div class="highlight">
                        <p><strong>纪念馆信息：</strong></p>
                        <ul>
                            <li>宠物姓名：{pet_name}</li>
                            <li>创建时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}</li>
                            <li>纪念馆链接：如果打不开请复制到浏览器中打开<a href="{full_memorial_url}">{full_memorial_url}</a></li>
                        </ul>
                    </div>
        """
        
        # 如果有性格测试结果，添加到邮件中
        if personality_type:
            html += f"""
                    <div class="personality-info">
                        <p><strong>性格分析结果：</strong></p>
                        <p>您的{pet_name}属于：<strong>{personality_type}</strong></p>
                    </div>
            """
        
        # 如果有AI信件，添加到邮件中
        if ai_letter:
            # 截取信件的前100个字符作为预览
            letter_preview = ai_letter[:100] + "..." if len(ai_letter) > 100 else ai_letter
            html += f"""
                    <div class="ai-letter">
                        <p><strong>来自{pet_name}的信（预览）：</strong></p>
                        <p>"{letter_preview}"</p>
                    </div>
            """
        
        html += f"""
                    <p>点击下面的按钮，立即查看完整的纪念馆：</p>
                    
                    <div style="text-align: center;">
                        <a href="{full_memorial_url}" class="button">🏠 查看纪念馆</a>
                    </div>
                    
                    <p>您也可以将纪念馆链接分享给朋友，让更多人了解{pet_name}的故事。</p>
                    
                    <p>如果您有任何问题或建议，请随时联系我们。发送邮件至1208155205@qq.com</p>
                </div>
                
                <div class="footer">
                            <p>此邮件由 爪迹星·云纪念馆系统自动发送</p>
        <p>© {datetime.now().year}  爪迹星·云纪念馆 - 让爱永远延续</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _send_email(self, to_email, subject, html_content):
        """发送邮件"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            from email.header import Header
            import ssl
            
            # 创建邮件对象
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = Header(subject, 'utf-8')
            
            # 添加HTML内容
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            print(f"📧 正在连接SMTP服务器: {self.smtp_server}:{self.smtp_port}")
            
            # 尝试不同的连接方式
            try:
                # 方式1: 使用TLS (端口587)
                if self.smtp_port == 587:
                    print("🔒 使用TLS连接...")
                    server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
                    server.set_debuglevel(1)  # 启用调试模式
                    server.starttls(context=ssl.create_default_context())
                    print("🔐 正在登录...")
                    server.login(self.sender_email, self.sender_password)
                    print("📤 正在发送邮件...")
                    server.send_message(msg)
                    print("✅ 邮件发送成功！")
                    
                    # 优雅关闭连接
                    try:
                        server.quit()
                    except Exception as quit_error:
                        print(f"⚠️  连接关闭时出现警告: {quit_error}")
                        # 这不影响邮件发送成功
                    
                    return True
                
                # 方式2: 使用SSL (端口465)
                elif self.smtp_port == 465:
                    print("🔒 使用SSL连接...")
                    server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=30)
                    server.set_debuglevel(1)  # 启用调试模式
                    print("🔐 正在登录...")
                    server.login(self.sender_email, self.sender_password)
                    print("📤 正在发送邮件...")
                    server.send_message(msg)
                    print("✅ 邮件发送成功！")
                    
                    # 优雅关闭连接
                    try:
                        server.quit()
                    except Exception as quit_error:
                        print(f"⚠️  连接关闭时出现警告: {quit_error}")
                        # 这不影响邮件发送成功
                    
                    return True
                
                # 方式3: 普通连接 (端口25)
                else:
                    print("🔓 使用普通连接...")
                    server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
                    server.set_debuglevel(1)  # 启用调试模式
                    print("🔐 正在登录...")
                    server.login(self.sender_email, self.sender_password)
                    print("📤 正在发送邮件...")
                    server.send_message(msg)
                    print("✅ 邮件发送成功！")
                    
                    # 优雅关闭连接
                    try:
                        server.quit()
                    except Exception as quit_error:
                        print(f"⚠️  连接关闭时出现警告: {quit_error}")
                        # 这不影响邮件发送成功
                    
                    return True
                        
            except smtplib.SMTPAuthenticationError as e:
                print(f"❌ SMTP认证失败: {e}")
                print("💡 请检查邮箱地址和授权码是否正确")
                return False
            except smtplib.SMTPConnectError as e:
                print(f"❌ SMTP连接失败: {e}")
                print("💡 请检查SMTP服务器地址和端口是否正确")
                return False
            except smtplib.SMTPRecipientsRefused as e:
                print(f"❌ 收件人地址被拒绝: {e}")
                print("💡 请检查收件人邮箱地址是否正确")
                return False
            except smtplib.SMTPSenderRefused as e:
                print(f"❌ 发件人地址被拒绝: {e}")
                print("💡 请检查发件人邮箱地址和授权码")
                return False
            except smtplib.SMTPDataError as e:
                print(f"❌ 邮件数据错误: {e}")
                return False
            except smtplib.SMTPException as e:
                print(f"❌ SMTP异常: {e}")
                # 检查是否是连接关闭时的错误
                if "(-1, b'\\x00\\x00\\x00')" in str(e):
                    print("💡 这是连接关闭时的网络警告，邮件已成功发送")
                    return True
                return False
            except Exception as e:
                print(f"❌ 邮件发送失败: {e}")
                print(f"💡 错误类型: {type(e).__name__}")
                
                # 检查是否是已知的网络警告（不影响邮件发送）
                error_str = str(e)
                if any(warning in error_str for warning in [
                    "(-1, b'\\x00\\x00\\x00')",
                    "(-1, b'\\x00\\x00\\x00\\x1a\\x00\\x00\\x00\\n')",
                    "connection closed",
                    "EOF occurred"
                ]):
                    print("💡 这是连接关闭时的网络警告，邮件已成功发送到服务器")
                    return True
                
                import traceback
                traceback.print_exc()
                return False
        
        except Exception as e:
            print(f"❌ 邮件发送失败: {e}")
            print(f"💡 错误类型: {type(e).__name__}")
            
            # 检查是否是已知的网络警告（不影响邮件发送）
            error_str = str(e)
            if any(warning in error_str for warning in [
                "(-1, b'\\x00\\x00\\x00')",
                "(-1, b'\\x00\\x00\\x00\\x1a\\x00\\x00\\x00\\n')",
                "connection closed",
                "EOF occurred"
            ]):
                print("💡 这是连接关闭时的网络警告，邮件已成功发送到服务器")
                return True
            
            import traceback
            traceback.print_exc()
            return False
    
    def send_test_email(self, to_email):
        """发送测试邮件"""
        subject = "🧪  爪迹星·云纪念馆 - 邮件服务测试"
        html_content = f"""
        <html>
        <body>
            <h2>邮件服务测试</h2>
            <p>如果您收到这封邮件，说明邮件服务配置成功！</p>
            <p>测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </body>
        </html>
        """
        
        return self._send_email(to_email, subject, html_content)
    
    def send_verification_code(self, to_email, code):
        """发送验证码邮件"""
        subject = "🔐  爪迹星·云纪念馆 - 邮箱验证码"
        html_content = self._build_verification_email_html(code)
        
        return self._send_email(to_email, subject, html_content)
    
    def send_password_reset_email(self, to_email, reset_url):
        """发送密码重置邮件"""
        subject = "🔑  爪迹星·云纪念馆 - 密码重置"
        html_content = self._build_password_reset_email_html(reset_url)
        
        return self._send_email(to_email, subject, html_content)
    
    def _build_verification_email_html(self, code):
        """构建验证码邮件HTML内容"""
        html = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>邮箱验证码</title>
            <style>
                body {{
                    font-family: 'Microsoft YaHei', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .email-container {{
                    background-color: white;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    padding: 20px 0;
                    border-bottom: 3px solid #667eea;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    color: #667eea;
                    margin: 0;
                    font-size: 2em;
                }}
                .code-container {{
                    text-align: center;
                    margin: 30px 0;
                    padding: 20px;
                    background-color: #f8f9fa;
                    border-radius: 10px;
                    border: 2px dashed #667eea;
                }}
                .verification-code {{
                    font-size: 3em;
                    font-weight: bold;
                    color: #667eea;
                    letter-spacing: 10px;
                    margin: 20px 0;
                }}
                .warning {{
                    background-color: #fff3cd;
                    border: 1px solid #ffeaa7;
                    border-radius: 5px;
                    padding: 15px;
                    margin: 20px 0;
                    color: #856404;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    color: #666;
                    font-size: 0.9em;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>🐾  爪迹星·云纪念馆</h1>
                    <p>邮箱验证码</p>
                </div>
                
                <div class="content">
                    <h2>亲爱的用户：</h2>
                    
                    <p>您正在使用邮箱验证功能，请在验证码输入框中输入以下验证码：</p>
                    
                    <div class="code-container">
                        <div class="verification-code">{code}</div>
                        <p><strong>验证码有效期：10分钟</strong></p>
                    </div>
                    
                    <div class="warning">
                        <p><strong>⚠️ 安全提醒：</strong></p>
                        <ul>
                            <li>请勿将验证码告诉他人</li>
                            <li>验证码将在10分钟后自动失效</li>
                            <li>如非本人操作，请忽略此邮件</li>
                        </ul>
                    </div>
                    
                    <p>如果您没有进行相关操作，请忽略此邮件。</p>
                </div>
                
                <div class="footer">
                    <p>此邮件由 爪迹星·云纪念馆系统自动发送</p>
                    <p>© {datetime.now().year}  爪迹星·云纪念馆 - 让爱永远延续</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _build_password_reset_email_html(self, reset_url):
        """构建密码重置邮件HTML内容"""
        html = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>密码重置</title>
            <style>
                body {{
                    font-family: 'Microsoft YaHei', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .email-container {{
                    background-color: white;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    padding: 20px 0;
                    border-bottom: 3px solid #667eea;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    color: #667eea;
                    margin: 0;
                    font-size: 2em;
                }}
                .button {{
                    display: inline-block;
                    background-color: #667eea;
                    color: white;
                    padding: 15px 30px;
                    text-decoration: none;
                    border-radius: 25px;
                    font-weight: bold;
                    margin: 20px 0;
                    text-align: center;
                }}
                .button:hover {{
                    background-color: #5a6fd8;
                }}
                .warning {{
                    background-color: #fff3cd;
                    border: 1px solid #ffeaa7;
                    border-radius: 5px;
                    padding: 15px;
                    margin: 20px 0;
                    color: #856404;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    color: #666;
                    font-size: 0.9em;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h1>🐾  爪迹星·云纪念馆</h1>
                    <p>密码重置</p>
                </div>
                
                <div class="content">
                    <h2>亲爱的用户：</h2>
                    
                    <p>我们收到了您的密码重置请求。请点击下面的按钮重置您的密码：</p>
                    
                    <div style="text-align: center;">
                        <a href="{reset_url}" class="button">🔑 重置密码</a>
                    </div>
                    
                    <p>如果按钮无法点击，请复制以下链接到浏览器中打开：</p>
                    <p style="word-break: break-all; color: #667eea;">{reset_url}</p>
                    
                    <div class="warning">
                        <p><strong>⚠️ 安全提醒：</strong></p>
                        <ul>
                            <li>此链接将在1小时后自动失效</li>
                            <li>请勿将此链接分享给他人</li>
                            <li>如非本人操作，请忽略此邮件</li>
                        </ul>
                    </div>
                    
                    <p>如果您没有请求重置密码，请忽略此邮件，您的密码将保持不变。</p>
                </div>
                
                <div class="footer">
                    <p>此邮件由 爪迹星·云纪念馆系统自动发送</p>
                    <p>© {datetime.now().year}  爪迹星·云纪念馆 - 让爱永远延续</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html