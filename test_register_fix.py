#!/usr/bin/env python3
"""
测试注册功能修复
"""

import requests
import json
import time

# 服务器地址
BASE_URL = "http://localhost:8000"

def test_register_with_different_emails():
    """测试使用不同邮箱注册"""
    print("=== 测试注册功能修复 ===")
    
    # 测试多个不同的邮箱
    test_emails = [
        "test1@example.com",
        "test2@example.com", 
        "test3@example.com",
        "user123@gmail.com",
        "demo@qq.com"
    ]
    
    for i, email in enumerate(test_emails, 1):
        print(f"\n--- 测试 {i}: {email} ---")
        
        register_data = {
            "email": email,
            "password": "123456"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
            result = response.json()
            
            print(f"状态码: {response.status_code}")
            print(f"响应: {result}")
            
            if result.get("success"):
                print("✅ 注册成功")
            else:
                print(f"❌ 注册失败: {result.get('message')}")
                
        except Exception as e:
            print(f"❌ 请求失败: {e}")
        
        # 等待一秒再测试下一个
        time.sleep(1)

def test_duplicate_email():
    """测试重复邮箱注册"""
    print("\n=== 测试重复邮箱注册 ===")
    
    email = "duplicate@test.com"
    password = "123456"
    
    # 第一次注册
    print(f"第一次注册: {email}")
    register_data = {"email": email, "password": password}
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        result = response.json()
        print(f"第一次注册结果: {result}")
    except Exception as e:
        print(f"第一次注册失败: {e}")
        return
    
    # 第二次注册相同邮箱
    print(f"\n第二次注册相同邮箱: {email}")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        result = response.json()
        print(f"第二次注册结果: {result}")
        
        if not result.get("success") and "已存在" in result.get("message", ""):
            print("✅ 正确阻止了重复邮箱注册")
        else:
            print("❌ 应该阻止重复邮箱注册")
            
    except Exception as e:
        print(f"第二次注册失败: {e}")

def test_login():
    """测试登录功能"""
    print("\n=== 测试登录功能 ===")
    
    login_data = {
        "email": "test1@example.com",
        "password": "123456"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        result = response.json()
        
        print(f"登录结果: {result}")
        
        if result.get("success"):
            print("✅ 登录成功")
            return result.get("session_token")
        else:
            print(f"❌ 登录失败: {result.get('message')}")
            
    except Exception as e:
        print(f"❌ 登录请求失败: {e}")
    
    return None

def main():
    """主测试函数"""
    print("开始测试注册功能修复...")
    print("=" * 50)
    
    # 测试不同邮箱注册
    test_register_with_different_emails()
    
    # 测试重复邮箱注册
    test_duplicate_email()
    
    # 测试登录
    session_token = test_login()
    
    print("\n" + "=" * 50)
    print("=== 测试完成 ===")

if __name__ == "__main__":
    main()
