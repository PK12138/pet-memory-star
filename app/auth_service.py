import re
from typing import Optional, Dict, Any
from database import Database

class AuthService:
    def __init__(self, db: Database):
        self.db = db
    
    def validate_username(self, username: str) -> Dict[str, Any]:
        """验证用户名（已废弃，保留兼容性）"""
        return {"valid": True, "message": "用户名验证已废弃"}
    
    def validate_email(self, email: str) -> Dict[str, Any]:
        """验证邮箱"""
        if not email:
            return {"valid": False, "message": "邮箱不能为空"}
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return {"valid": False, "message": "邮箱格式不正确"}
        
        return {"valid": True, "message": "邮箱格式正确"}
    
    def validate_password(self, password: str) -> Dict[str, Any]:
        """验证密码"""
        if not password:
            return {"valid": False, "message": "密码不能为空"}
        
        if len(password) < 6:
            return {"valid": False, "message": "密码长度至少6个字符"}
        
        if len(password) > 50:
            return {"valid": False, "message": "密码长度不能超过50个字符"}
        
        return {"valid": True, "message": "密码格式正确"}
    
    def register_user(self, email: str, password: str) -> Dict[str, Any]:
        """注册用户"""
        # 验证输入
        email_validation = self.validate_email(email)
        if not email_validation["valid"]:
            return {"success": False, "message": email_validation["message"]}
        
        password_validation = self.validate_password(password)
        if not password_validation["valid"]:
            return {"success": False, "message": password_validation["message"]}
        
        # 创建用户
        user_id = self.db.create_user(email, password)
        
        if user_id:
            return {
                "success": True, 
                "message": "注册成功！",
                "user_id": user_id
            }
        else:
            return {"success": False, "message": "邮箱已存在"}
    
    def login_user(self, email: str, password: str, ip_address: str = None, user_agent: str = None) -> Dict[str, Any]:
        """用户登录"""
        if not email or not password:
            return {"success": False, "message": "邮箱和密码不能为空"}
        
        # 验证用户
        user = self.db.verify_user(email, password)
        
        if not user:
            return {"success": False, "message": "邮箱或密码错误"}
        
        if not user["is_active"]:
            return {"success": False, "message": "账户已被禁用"}
        
        # 创建会话
        session_token = self.db.create_session(user["id"], ip_address, user_agent)
        
        return {
            "success": True,
            "message": "登录成功！",
            "session_token": session_token,
            "user": user
        }
    
    def logout_user(self, session_token: str) -> Dict[str, Any]:
        """用户登出"""
        if self.db.delete_session(session_token):
            return {"success": True, "message": "登出成功"}
        else:
            return {"success": False, "message": "登出失败"}
    
    def get_current_user(self, session_token: str) -> Optional[Dict[str, Any]]:
        """获取当前用户信息"""
        if not session_token:
            return None
        
        user = self.db.get_user_by_session(session_token)
        if user:
            # 获取用户等级信息
            level_info = self.db.get_user_level_info(user["user_level"])
            if level_info:
                user["level_info"] = {
                    "name": level_info[1],
                    "max_memorials": level_info[2],
                    "max_photos": level_info[3],
                    "can_use_ai": level_info[4],
                    "can_export": level_info[5],
                    "can_custom_domain": level_info[6],
                    "description": level_info[9]
                }
        
        return user
    
    def check_user_permission(self, user_id: int, permission: str) -> bool:
        """检查用户权限"""
        user = self.db.get_user_by_id(user_id)  # 修复：直接通过用户ID查询
        if not user:
            return False
        
        level_info = self.db.get_user_level_info(user["user_level"])
        if not level_info:
            return False
        
        # 权限映射
        permissions = {
            "ai": level_info[4],  # can_use_ai
            "export": level_info[5],  # can_export
            "custom_domain": level_info[6],  # can_custom_domain
        }
        
        return permissions.get(permission, False)
    
    def can_create_memorial(self, user_id: int) -> Dict[str, Any]:
        """检查用户是否可以创建纪念馆"""
        user = self.db.get_user_by_id(user_id)  # 修复：直接通过用户ID查询
        if not user:
            return {"can_create": False, "message": "用户未登录"}
        
        level_info = self.db.get_user_level_info(user["user_level"])
        if not level_info:
            return {"can_create": False, "message": "用户等级信息错误"}
        
        max_memorials = level_info[2]
        if max_memorials == -1:  # 无限
            return {"can_create": True, "message": "可以创建纪念馆"}
        
        current_count = self.db.get_user_memorial_count(user_id)
        if current_count >= max_memorials:
            return {
                "can_create": False, 
                "message": f"已达到最大纪念馆数量限制({max_memorials}个)，请升级会员"
            }
        
        return {"can_create": True, "message": "可以创建纪念馆"}
    
    def get_user_dashboard_data(self, user_id: int) -> Dict[str, Any]:
        """获取用户仪表板数据"""
        user = self.db.get_user_by_id(user_id)  # 修复：直接通过用户ID查询
        if not user:
            return {}
        
        level_info = self.db.get_user_level_info(user["user_level"])
        memorials = self.db.get_user_memorials(user_id)
        memorial_count = self.db.get_user_memorial_count(user_id)
        
        return {
            "user": user,
            "level_info": {
                "name": level_info[1] if level_info else "未知",
                "max_memorials": level_info[2] if level_info else 1,
                "max_photos": level_info[3] if level_info else 10,
                "can_use_ai": level_info[4] if level_info else False,
                "can_export": level_info[5] if level_info else False,
                "can_custom_domain": level_info[6] if level_info else False,
                "description": level_info[9] if level_info else ""
            },
            "memorials": memorials,
            "memorial_count": memorial_count,
            "can_create_more": memorial_count < (level_info[2] if level_info and level_info[2] != -1 else float('inf'))
        }
