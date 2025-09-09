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
        result = self.db.create_user(email, password)
        
        if result and isinstance(result, dict):
            return {
                "success": True, 
                "message": "注册成功！请检查邮箱完成验证。",
                "user_id": result["user_id"],
                "verification_token": result["verification_token"]
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
    
    def verify_email(self, verification_token: str) -> Dict[str, Any]:
        """验证邮箱"""
        if not verification_token:
            return {"success": False, "message": "验证令牌不能为空"}
        
        result = self.db.verify_email(verification_token)
        if result:
            return {
                "success": True,
                "message": "邮箱验证成功！现在可以正常使用所有功能。",
                "user_id": result["user_id"],
                "email": result["email"]
            }
        else:
            return {"success": False, "message": "验证令牌无效或已过期"}
    
    def resend_verification_email(self, email: str) -> Dict[str, Any]:
        """重新发送验证邮件"""
        if not email:
            return {"success": False, "message": "邮箱不能为空"}
        
        verification_token = self.db.resend_verification_email(email)
        if verification_token:
            return {
                "success": True,
                "message": "验证邮件已重新发送，请检查邮箱。",
                "verification_token": verification_token
            }
        else:
            return {"success": False, "message": "邮箱不存在或已验证"}
    
    def request_password_reset(self, email: str) -> Dict[str, Any]:
        """请求密码重置"""
        if not email:
            return {"success": False, "message": "邮箱不能为空"}
        
        reset_token = self.db.create_password_reset_token(email)
        if reset_token:
            return {
                "success": True,
                "message": "密码重置邮件已发送，请检查邮箱。",
                "reset_token": reset_token
            }
        else:
            return {"success": False, "message": "邮箱不存在或未验证"}
    
    def reset_password(self, reset_token: str, new_password: str) -> Dict[str, Any]:
        """重置密码"""
        if not reset_token:
            return {"success": False, "message": "重置令牌不能为空"}
        
        password_validation = self.validate_password(new_password)
        if not password_validation["valid"]:
            return {"success": False, "message": password_validation["message"]}
        
        if self.db.reset_password(reset_token, new_password):
            return {
                "success": True,
                "message": "密码重置成功！请使用新密码登录。"
            }
        else:
            return {"success": False, "message": "重置令牌无效或已过期"}
    
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
    
    def can_upload_photo(self, user_id: int, memorial_id: str) -> Dict[str, Any]:
        """检查用户是否可以上传照片到指定纪念馆"""
        user = self.db.get_user_by_id(user_id)
        if not user:
            return {"can_upload": False, "message": "用户未登录"}
        
        # 检查邮箱是否已验证
        if not user.get("email_verified", False):
            return {"can_upload": False, "message": "请先验证邮箱"}
        
        # 检查纪念馆是否属于该用户
        memorial = self.db.get_memorial_by_id(memorial_id)
        if not memorial or memorial["user_id"] != user_id:
            return {"can_upload": False, "message": "无权访问该纪念馆"}
        
        level_info = self.db.get_user_level_info(user["user_level"])
        if not level_info:
            return {"can_upload": False, "message": "用户等级信息错误"}
        
        max_photos = level_info[3]
        if max_photos == -1:  # 无限
            return {"can_upload": True, "message": "可以上传照片"}
        
        current_count = self.db.get_memorial_photo_count(memorial_id)
        if current_count >= max_photos:
            return {
                "can_upload": False, 
                "message": f"已达到最大照片数量限制({max_photos}张)，请升级会员",
                "current_count": current_count,
                "max_count": max_photos
            }
        
        return {"can_upload": True, "message": "可以上传照片"}
    
    def can_use_ai_feature(self, user_id: int) -> Dict[str, Any]:
        """检查用户是否可以使用AI功能"""
        user = self.db.get_user_by_id(user_id)
        if not user:
            return {"can_use": False, "message": "用户未登录"}
        
        # 检查邮箱是否已验证
        if not user.get("email_verified", False):
            return {"can_use": False, "message": "请先验证邮箱"}
        
        level_info = self.db.get_user_level_info(user["user_level"])
        if not level_info:
            return {"can_use": False, "message": "用户等级信息错误"}
        
        can_use_ai = level_info[4]
        if can_use_ai:
            return {"can_use": True, "message": "可以使用AI功能"}
        else:
            return {"can_use": False, "message": "当前等级不支持AI功能，请升级会员"}
    
    def can_export_data(self, user_id: int) -> Dict[str, Any]:
        """检查用户是否可以导出数据"""
        user = self.db.get_user_by_id(user_id)
        if not user:
            return {"can_export": False, "message": "用户未登录"}
        
        # 检查邮箱是否已验证
        if not user.get("email_verified", False):
            return {"can_export": False, "message": "请先验证邮箱"}
        
        level_info = self.db.get_user_level_info(user["user_level"])
        if not level_info:
            return {"can_export": False, "message": "用户等级信息错误"}
        
        can_export = level_info[5]
        if can_export:
            return {"can_export": True, "message": "可以导出数据"}
        else:
            return {"can_export": False, "message": "当前等级不支持数据导出，请升级会员"}
    
    def upgrade_user_level(self, user_id: int, new_level: int) -> Dict[str, Any]:
        """升级用户等级"""
        user = self.db.get_user_by_id(user_id)
        if not user:
            return {"success": False, "message": "用户不存在"}
        
        level_info = self.db.get_user_level_info(new_level)
        if not level_info:
            return {"success": False, "message": "目标等级不存在"}
        
        if new_level <= user["user_level"]:
            return {"success": False, "message": "只能升级到更高等级"}
        
        success = self.db.update_user_level(user_id, new_level)
        if success:
            return {
                "success": True, 
                "message": f"成功升级到{level_info[1]}",
                "new_level": new_level,
                "level_info": {
                    "name": level_info[1],
                    "max_memorials": level_info[2],
                    "max_photos": level_info[3],
                    "can_use_ai": level_info[4],
                    "can_export": level_info[5],
                    "can_custom_domain": level_info[6],
                    "description": level_info[9]
                }
            }
        else:
            return {"success": False, "message": "升级失败"}
    
    def get_user_dashboard_data(self, user_id: int) -> Dict[str, Any]:
        """获取用户仪表板数据"""
        user = self.db.get_user_by_id(user_id)
        if not user:
            return {"success": False, "message": "用户不存在"}
        
        # 获取用户等级信息
        level_info = self.db.get_user_level_info(user["user_level"])
        if not level_info:
            return {"success": False, "message": "用户等级信息错误"}
        
        # 获取用户纪念馆数量
        memorial_count = self.db.get_user_memorial_count(user_id)
        
        # 获取用户照片总数
        total_photos = 0
        user_memorials = self.db.get_user_memorials(user_id)
        for memorial in user_memorials:
            total_photos += self.db.get_memorial_photo_count(memorial["id"])
        
        return {
            "success": True,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "user_level": user["user_level"],
                "level_name": level_info[1],
                "memorial_count": memorial_count,
                "max_memorials": level_info[2],
                "total_photos": total_photos,
                "max_photos": level_info[3],
                "can_use_ai": level_info[4],
                "can_export": level_info[5],
                "can_custom_domain": level_info[6],
                "level_description": level_info[9],
                "email_verified": user.get("email_verified", False)
            }
        }
