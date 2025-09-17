"""
权限控制中间件
统一处理用户权限验证和功能限制提示
"""
from fastapi import Request, HTTPException, Header
from typing import Optional, Dict, Any
from auth_service import AuthService
from database import Database

class PermissionMiddleware:
    """权限控制中间件"""
    
    def __init__(self, db: Database):
        self.auth_service = AuthService(db)
        self.db = db
    
    async def check_permission(self, request: Request, required_permission: str, 
                             session_token: Optional[str] = Header(None, alias="x-session-token")) -> Dict[str, Any]:
        """检查用户权限"""
        try:
            # 获取当前用户
            user = self.auth_service.get_current_user(session_token)
            if not user:
                return {
                    "success": False,
                    "message": "用户未登录",
                    "action": "redirect_to_login"
                }
            
            # 检查具体权限
            permission_result = self._check_specific_permission(user, required_permission)
            
            if not permission_result["success"]:
                return {
                    "success": False,
                    "message": permission_result["message"],
                    "action": permission_result.get("action", "show_upgrade_prompt"),
                    "user": user,
                    "permission_info": permission_result.get("permission_info")
                }
            
            return {
                "success": True,
                "user": user,
                "permission_info": permission_result.get("permission_info")
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"权限检查失败: {str(e)}",
                "action": "show_error"
            }
    
    def _check_specific_permission(self, user: Dict[str, Any], permission: str) -> Dict[str, Any]:
        """检查具体权限"""
        user_id = user["id"]
        
        if permission == "create_memorial":
            return self._check_create_memorial_permission(user_id)
        elif permission == "upload_photo":
            return self._check_upload_photo_permission(user_id)
        elif permission == "use_ai_feature":
            return self._check_ai_feature_permission(user_id)
        elif permission == "export_data":
            return self._check_export_permission(user_id)
        elif permission == "unlimited_memorials":
            return self._check_unlimited_memorials_permission(user_id)
        elif permission == "unlimited_photos":
            return self._check_unlimited_photos_permission(user_id)
        else:
            return {
                "success": False,
                "message": f"未知权限类型: {permission}",
                "action": "show_error"
            }
    
    def _check_create_memorial_permission(self, user_id: int) -> Dict[str, Any]:
        """检查创建纪念馆权限"""
        try:
            # 获取用户等级信息
            level_info = self.db.get_user_level_info(user_id)
            if not level_info:
                return {
                    "success": False,
                    "message": "无法获取用户等级信息",
                    "action": "show_error"
                }
            
            # 获取用户当前纪念馆数量
            current_count = len(self.db.get_user_memorials(user_id))
            max_allowed = level_info["max_memorials"]
            
            if max_allowed == -1:  # 无限制
                return {
                    "success": True,
                    "permission_info": {
                        "current_count": current_count,
                        "max_allowed": "无限制",
                        "can_create": True
                    }
                }
            elif current_count < max_allowed:
                return {
                    "success": True,
                    "permission_info": {
                        "current_count": current_count,
                        "max_allowed": max_allowed,
                        "can_create": True,
                        "remaining": max_allowed - current_count
                    }
                }
            else:
                return {
                    "success": False,
                    "message": f"已达到纪念馆创建上限（{max_allowed}个），请升级会员",
                    "action": "show_upgrade_prompt",
                    "permission_info": {
                        "current_count": current_count,
                        "max_allowed": max_allowed,
                        "can_create": False,
                        "upgrade_benefit": f"升级后可创建无限纪念馆"
                    }
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"检查创建纪念馆权限失败: {str(e)}",
                "action": "show_error"
            }
    
    def _check_upload_photo_permission(self, user_id: int) -> Dict[str, Any]:
        """检查照片上传权限"""
        try:
            # 获取用户等级信息
            level_info = self.db.get_user_level_info(user_id)
            if not level_info:
                return {
                    "success": False,
                    "message": "无法获取用户等级信息",
                    "action": "show_error"
                }
            
            # 获取用户当前照片数量
            current_count = self.db.get_memorial_photo_count(user_id)
            max_allowed = level_info["max_photos"]
            
            if max_allowed == -1:  # 无限制
                return {
                    "success": True,
                    "permission_info": {
                        "current_count": current_count,
                        "max_allowed": "无限制",
                        "can_upload": True
                    }
                }
            elif current_count < max_allowed:
                return {
                    "success": True,
                    "permission_info": {
                        "current_count": current_count,
                        "max_allowed": max_allowed,
                        "can_upload": True,
                        "remaining": max_allowed - current_count
                    }
                }
            else:
                return {
                    "success": False,
                    "message": f"已达到照片上传上限（{max_allowed}张），请升级会员",
                    "action": "show_upgrade_prompt",
                    "permission_info": {
                        "current_count": current_count,
                        "max_allowed": max_allowed,
                        "can_upload": False,
                        "upgrade_benefit": f"升级后可上传无限照片"
                    }
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"检查照片上传权限失败: {str(e)}",
                "action": "show_error"
            }
    
    def _check_ai_feature_permission(self, user_id: int) -> Dict[str, Any]:
        """检查AI功能权限"""
        try:
            # 获取用户等级信息
            level_info = self.db.get_user_level_info(user_id)
            if not level_info:
                return {
                    "success": False,
                    "message": "无法获取用户等级信息",
                    "action": "show_error"
                }
            
            can_use_ai = level_info["can_use_ai"] == 1
            
            if can_use_ai:
                return {
                    "success": True,
                    "permission_info": {
                        "can_use_ai": True,
                        "feature_name": "AI智能功能"
                    }
                }
            else:
                return {
                    "success": False,
                    "message": "AI智能功能仅限高级用户使用，请升级会员",
                    "action": "show_upgrade_prompt",
                    "permission_info": {
                        "can_use_ai": False,
                        "feature_name": "AI智能功能",
                        "upgrade_benefit": "升级后可使用AI智能功能"
                    }
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"检查AI功能权限失败: {str(e)}",
                "action": "show_error"
            }
    
    def _check_export_permission(self, user_id: int) -> Dict[str, Any]:
        """检查数据导出权限"""
        try:
            # 获取用户等级信息
            level_info = self.db.get_user_level_info(user_id)
            if not level_info:
                return {
                    "success": False,
                    "message": "无法获取用户等级信息",
                    "action": "show_error"
                }
            
            can_export = level_info["can_export"] == 1
            
            if can_export:
                return {
                    "success": True,
                    "permission_info": {
                        "can_export": True,
                        "feature_name": "数据导出"
                    }
                }
            else:
                return {
                    "success": False,
                    "message": "数据导出功能仅限高级用户使用，请升级会员",
                    "action": "show_upgrade_prompt",
                    "permission_info": {
                        "can_export": False,
                        "feature_name": "数据导出",
                        "upgrade_benefit": "升级后可导出数据"
                    }
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"检查导出权限失败: {str(e)}",
                "action": "show_error"
            }
    
    def _check_unlimited_memorials_permission(self, user_id: int) -> Dict[str, Any]:
        """检查无限纪念馆权限"""
        try:
            level_info = self.db.get_user_level_info(user_id)
            if not level_info:
                return {
                    "success": False,
                    "message": "无法获取用户等级信息",
                    "action": "show_error"
                }
            
            has_unlimited = level_info["max_memorials"] == -1
            
            if has_unlimited:
                return {
                    "success": True,
                    "permission_info": {
                        "has_unlimited": True,
                        "feature_name": "无限纪念馆"
                    }
                }
            else:
                return {
                    "success": False,
                    "message": "无限纪念馆功能仅限高级用户使用，请升级会员",
                    "action": "show_upgrade_prompt",
                    "permission_info": {
                        "has_unlimited": False,
                        "feature_name": "无限纪念馆",
                        "upgrade_benefit": "升级后可创建无限纪念馆"
                    }
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"检查无限纪念馆权限失败: {str(e)}",
                "action": "show_error"
            }
    
    def _check_unlimited_photos_permission(self, user_id: int) -> Dict[str, Any]:
        """检查无限照片权限"""
        try:
            level_info = self.db.get_user_level_info(user_id)
            if not level_info:
                return {
                    "success": False,
                    "message": "无法获取用户等级信息",
                    "action": "show_error"
                }
            
            has_unlimited = level_info["max_photos"] == -1
            
            if has_unlimited:
                return {
                    "success": True,
                    "permission_info": {
                        "has_unlimited": True,
                        "feature_name": "无限照片"
                    }
                }
            else:
                return {
                    "success": False,
                    "message": "无限照片功能仅限高级用户使用，请升级会员",
                    "action": "show_upgrade_prompt",
                    "permission_info": {
                        "has_unlimited": False,
                        "feature_name": "无限照片",
                        "upgrade_benefit": "升级后可上传无限照片"
                    }
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"检查无限照片权限失败: {str(e)}",
                "action": "show_error"
            }
    
    def get_upgrade_prompt_data(self, permission_info: Dict[str, Any]) -> Dict[str, Any]:
        """获取升级提示数据"""
        return {
            "title": "功能限制",
            "message": permission_info.get("message", "此功能需要升级会员"),
            "feature_name": permission_info.get("feature_name", "高级功能"),
            "upgrade_benefit": permission_info.get("upgrade_benefit", "升级后可使用更多功能"),
            "current_usage": permission_info.get("current_count", 0),
            "max_allowed": permission_info.get("max_allowed", 0),
            "remaining": permission_info.get("remaining", 0)
        }
