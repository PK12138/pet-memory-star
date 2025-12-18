import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from .config import config

class EmailService:
    def __init__(self):
        self.smtp_server = config.SMTP_SERVER
        self.smtp_port = config.SMTP_PORT
        self.sender_email = config.SENDER_EMAIL
        self.sender_password = config.SENDER_PASSWORD
        self.base_url = config.BASE_URL
    
    def send_email_verification(self, to_email: str, verification_token: str) -> Dict[str, Any]:
        """发送邮箱验证邮件"""
        try:
            # 创建邮件内容
            subject = " 爪迹星·邮箱验证"
            
            # HTML邮件内容
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>邮箱验证</title>
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
                    .container {{
                        background-color: white;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        text-align: center;
                        margin-bottom: 30px;
                    }}
                    .logo {{
                        font-size: 24px;
                        font-weight: bold;
                        color: #667eea;
                        margin-bottom: 10px;
                    }}
                    .title {{
                        font-size: 20px;
                        color: #333;
                        margin-bottom: 20px;
                    }}
                    .content {{
                        margin-bottom: 30px;
                        line-height: 1.8;
                    }}
                    .button {{
                        display: inline-block;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 12px 30px;
                        text-decoration: none;
                        border-radius: 25px;
                        font-weight: bold;
                        margin: 20px 0;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #eee;
                        color: #666;
                        font-size: 14px;
                    }}
                    .warning {{
                        background-color: #fff3cd;
                        border: 1px solid #ffeaa7;
                        color: #856404;
                        padding: 15px;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">🐾  爪迹星</div>
                        <div class="title">邮箱验证</div>
                    </div>
                    
                    <div class="content">
                        <p>您好！感谢您注册 爪迹星·云纪念馆。</p>
                        <p>为了确保您的账户安全，请点击下面的按钮验证您的邮箱地址：</p>
                        
                        <div style="text-align: center;">
                            <a href="{self.base_url}/verify-email?token={verification_token}" class="button">
                                验证邮箱
                            </a>
                        </div>
                        
                        <p>如果按钮无法点击，请复制以下链接到浏览器地址栏：</p>
                        <p style="word-break: break-all; color: #667eea;">
                            {self.base_url}/verify-email?token={verification_token}
                        </p>
                        
                        <div class="warning">
                            <strong>⚠️ 安全提醒：</strong><br>
                            • 此链接24小时内有效<br>
                            • 请勿将验证链接分享给他人<br>
                            • 如果这不是您的操作，请忽略此邮件
                        </div>
                        
                        <p>验证成功后，您就可以使用 爪迹星的所有功能了！</p>
                    </div>
                    
                    <div class="footer">
                        <p>此邮件由系统自动发送，请勿回复</p>
                        <p>如有问题，请联系客服</p>
                        <p>© 2024  爪迹星·云纪念馆</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # 纯文本内容（备用）
            text_content = f"""
             爪迹星·邮箱验证
            
            您好！感谢您注册 爪迹星·云纪念馆。
            
            为了确保您的账户安全，请访问以下链接验证您的邮箱地址：
            {self.base_url}/verify-email?token={verification_token}
            
            此链接24小时内有效。
            
            验证成功后，您就可以使用 爪迹星的所有功能了！
            
            此邮件由系统自动发送，请勿回复。
            © 2024  爪迹星·云纪念馆
            """
            
            return self._send_email(to_email, subject, html_content, text_content)
            
        except Exception as e:
            return {"success": False, "message": f"发送验证邮件失败: {str(e)}"}
    
    def send_password_reset(self, to_email: str, reset_token: str) -> Dict[str, Any]:
        """发送密码重置邮件"""
        try:
            subject = " 爪迹星·密码重置"
            
            # HTML邮件内容
            html_content = f"""
            <!DOCTYPE html>
            <html>
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
                    .container {{
                        background-color: white;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        text-align: center;
                        margin-bottom: 30px;
                    }}
                    .logo {{
                        font-size: 24px;
                        font-weight: bold;
                        color: #667eea;
                        margin-bottom: 10px;
                    }}
                    .title {{
                        font-size: 20px;
                        color: #333;
                        margin-bottom: 20px;
                    }}
                    .content {{
                        margin-bottom: 30px;
                        line-height: 1.8;
                    }}
                    .button {{
                        display: inline-block;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 12px 30px;
                        text-decoration: none;
                        border-radius: 25px;
                        font-weight: bold;
                        margin: 20px 0;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #eee;
                        color: #666;
                        font-size: 14px;
                    }}
                    .warning {{
                        background-color: #fff3cd;
                        border: 1px solid #ffeaa7;
                        color: #856404;
                        padding: 15px;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                    .danger {{
                        background-color: #f8d7da;
                        border: 1px solid #f5c6cb;
                        color: #721c24;
                        padding: 15px;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">🐾  爪迹星</div>
                        <div class="title">密码重置</div>
                    </div>
                    
                    <div class="content">
                        <p>您好！我们收到了您的密码重置请求。</p>
                        <p>请点击下面的按钮重置您的密码：</p>
                        
                        <div style="text-align: center;">
                            <a href="{self.base_url}/reset-password?token={reset_token}" class="button">
                                重置密码
                            </a>
                        </div>
                        
                        <p>如果按钮无法点击，请复制以下链接到浏览器地址栏：</p>
                        <p style="word-break: break-all; color: #667eea;">
                            {self.base_url}/reset-password?token={reset_token}
                        </p>
                        
                        <div class="warning">
                            <strong>⚠️ 重要提醒：</strong><br>
                            • 此链接1小时内有效<br>
                            • 请勿将重置链接分享给他人<br>
                            • 重置成功后，旧密码将失效
                        </div>
                        
                        <div class="danger">
                            <strong>🚨 安全警告：</strong><br>
                            如果您没有请求密码重置，请立即忽略此邮件并检查账户安全。
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p>此邮件由系统自动发送，请勿回复</p>
                        <p>如有问题，请联系客服</p>
                        <p>© 2024  爪迹星·云纪念馆</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # 纯文本内容（备用）
            text_content = f"""
             爪迹星·密码重置
            
            您好！我们收到了您的密码重置请求。
            
            请访问以下链接重置您的密码：
            {self.base_url}/reset-password?token={reset_token}
            
            此链接1小时内有效。
            
            如果您没有请求密码重置，请忽略此邮件。
            
            此邮件由系统自动发送，请勿回复。
            © 2024  爪迹星·云纪念馆
            """
            
            return self._send_email(to_email, subject, html_content, text_content)
            
        except Exception as e:
            return {"success": False, "message": f"发送重置邮件失败: {str(e)}"}
    
    def send_verification_code(self, to_email: str, verification_code: str) -> bool:
        """发送验证码邮件"""
        try:
            subject = " 爪迹星·密码重置验证码"
            
            # HTML邮件内容
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>密码重置验证码</title>
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
                    .container {{
                        background-color: white;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        text-align: center;
                        margin-bottom: 30px;
                    }}
                    .logo {{
                        font-size: 24px;
                        font-weight: bold;
                        color: #667eea;
                        margin-bottom: 10px;
                    }}
                    .verification-code {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 20px;
                        border-radius: 10px;
                        text-align: center;
                        margin: 20px 0;
                        font-size: 32px;
                        font-weight: bold;
                        letter-spacing: 5px;
                    }}
                    .warning {{
                        background-color: #fff3cd;
                        border: 1px solid #ffeaa7;
                        color: #856404;
                        padding: 15px;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        color: #666;
                        font-size: 14px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">🔑  爪迹星·云纪念馆</div>
                        <h1>密码重置验证码</h1>
                    </div>
                    
                    <p>您好，</p>
                    <p>您正在重置 爪迹星·云纪念馆账户的密码，请使用以下验证码完成重置：</p>
                    
                    <div class="verification-code">
                        {verification_code}
                    </div>
                    
                    <div class="warning">
                        <strong>⚠️ 安全提示：</strong>
                        <ul>
                            <li>此验证码有效期为10分钟</li>
                            <li>请勿将验证码泄露给他人</li>
                            <li>如非本人操作，请忽略此邮件</li>
                        </ul>
                    </div>
                    
                    <p>如果您没有请求重置密码，请忽略此邮件。</p>
                    
                    <div class="footer">
                        <p>此邮件由系统自动发送，请勿回复</p>
                        <p>© 2024  爪迹星·云纪念馆</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # 纯文本内容
            text_content = f"""
             爪迹星·云纪念馆 - 密码重置验证码
            
            您好，
            
            您正在重置 爪迹星·云纪念馆账户的密码，请使用以下验证码完成重置：
            
            验证码：{verification_code}
            
            安全提示：
            - 此验证码有效期为10分钟
            - 请勿将验证码泄露给他人
            - 如非本人操作，请忽略此邮件
            
            如果您没有请求重置密码，请忽略此邮件。
            
            此邮件由系统自动发送，请勿回复
            © 2024  爪迹星·云纪念馆
            """
            
            result = self._send_email(to_email, subject, html_content, text_content)
            return result.get("success", False)
            
        except Exception as e:
            print(f"发送验证码邮件失败: {str(e)}")
            return False
    
    def _send_email(self, to_email: str, subject: str, html_content: str, text_content: str) -> Dict[str, Any]:
        """发送邮件的通用方法"""
        try:
            # 创建邮件
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = to_email
            
            # 添加纯文本和HTML内容
            text_part = MIMEText(text_content, "plain", "utf-8")
            html_part = MIMEText(html_content, "html", "utf-8")
            
            message.attach(text_part)
            message.attach(html_part)
            
            # 创建SSL连接
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                
                # 发送邮件
                server.sendmail(self.sender_email, to_email, message.as_string())
            
            return {"success": True, "message": "邮件发送成功"}
            
        except smtplib.SMTPAuthenticationError:
            return {"success": False, "message": "邮箱认证失败，请检查邮箱配置"}
        except smtplib.SMTPRecipientsRefused:
            return {"success": False, "message": "收件人邮箱地址无效"}
        except smtplib.SMTPServerDisconnected:
            return {"success": False, "message": "邮件服务器连接断开"}
        except Exception as e:
            return {"success": False, "message": f"发送邮件失败: {str(e)}"}
    
    def test_connection(self) -> Dict[str, Any]:
        """测试邮件服务器连接"""
        try:
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
            
            return {"success": True, "message": "邮件服务器连接成功"}
            
        except Exception as e:
            return {"success": False, "message": f"邮件服务器连接失败: {str(e)}"}
