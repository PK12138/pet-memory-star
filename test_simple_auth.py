#!/usr/bin/env python3
"""
简化版用户认证系统测试脚本
"""

import requests
import json

# 服务器地址
BASE_URL = "http://localhost:8000"

def test_register():
    """测试用户注册"""
    print("=== 测试用户注册 ===")
    
    register_data = {
        "email": "test@example.com",
        "password": "123456"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
    result = response.json()
    
    print(f"注册结果: {result}")
    return result.get("success", False)

def test_login():
    """测试用户登录"""
    print("\n=== 测试用户登录 ===")
    
    login_data = {
        "email": "test@example.com",
        "password": "123456"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    result = response.json()
    
    print(f"登录结果: {result}")
    
    if result.get("success"):
        return result.get("session_token")
    return None

def test_get_user_info(session_token):
    """测试获取用户信息"""
    print("\n=== 测试获取用户信息 ===")
    
    headers = {"Authorization": f"Bearer {session_token}"}
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    result = response.json()
    
    print(f"用户信息: {json.dumps(result, indent=2, ensure_ascii=False)}")
    return result.get("success", False)

def test_can_create_memorial(session_token):
    """测试检查是否可以创建纪念馆"""
    print("\n=== 测试检查是否可以创建纪念馆 ===")
    
    headers = {"Authorization": f"Bearer {session_token}"}
    response = requests.get(f"{BASE_URL}/api/auth/can-create-memorial", headers=headers)
    result = response.json()
    
    print(f"是否可以创建纪念馆: {result}")
    return result.get("can_create", False)

def test_logout(session_token):
    """测试用户登出"""
    print("\n=== 测试用户登出 ===")
    
    headers = {"Authorization": f"Bearer {session_token}"}
    response = requests.post(f"{BASE_URL}/api/auth/logout", headers=headers)
    result = response.json()
    
    print(f"登出结果: {result}")
    return result.get("success", False)

def main():
    """主测试函数"""
    print("开始测试简化版用户认证系统...")
    print("=" * 50)
    
    # 测试注册
    if not test_register():
        print("注册失败，停止测试")
        return
    
    # 测试登录
    session_token = test_login()
    if not session_token:
        print("登录失败，停止测试")
        return
    
    # 测试获取用户信息
    test_get_user_info(session_token)
    
    # 测试检查是否可以创建纪念馆
    test_can_create_memorial(session_token)
    
    # 测试登出
    test_logout(session_token)
    
    print("\n" + "=" * 50)
    print("=== 测试完成 ===")

if __name__ == "__main__":
    main()
