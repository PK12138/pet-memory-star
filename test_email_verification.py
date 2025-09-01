#!/usr/bin/env python3
"""
测试邮箱验证码和密码重置功能
"""

import requests
import json
import time

# 服务器地址
BASE_URL = "http://42.193.230.145"

def test_send_verification_code():
    """测试发送验证码"""
    print("=== 测试发送验证码 ===")
    
    # 测试邮箱
    test_email = "1208155205@qq.com"  # 使用您的QQ邮箱进行测试
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/send-verification-code", 
                               json={"email": test_email})
        result = response.json()
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {result}")
        
        if result.get("success"):
            print("✅ 验证码发送成功")
            return True
        else:
            print(f"❌ 验证码发送失败: {result.get('message')}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_reset_password():
    """测试密码重置"""
    print("\n=== 测试密码重置 ===")
    
    # 这里需要手动输入验证码，因为验证码是随机生成的
    test_email = "1208155205@qq.com"
    verification_code = input("请输入收到的验证码: ").strip()
    new_password = "newpassword123"
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/reset-password", 
                               json={
                                   "email": test_email,
                                   "verification_code": verification_code,
                                   "new_password": new_password
                               })
        result = response.json()
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {result}")
        
        if result.get("success"):
            print("✅ 密码重置成功")
            return True
        else:
            print(f"❌ 密码重置失败: {result.get('message')}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_login_with_new_password():
    """测试使用新密码登录"""
    print("\n=== 测试新密码登录 ===")
    
    test_email = "1208155205@qq.com"
    new_password = "newpassword123"
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", 
                               json={
                                   "email": test_email,
                                   "password": new_password
                               })
        result = response.json()
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {result}")
        
        if result.get("success"):
            print("✅ 新密码登录成功")
            return True
        else:
            print(f"❌ 新密码登录失败: {result.get('message')}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_forgot_password_page():
    """测试忘记密码页面"""
    print("\n=== 测试忘记密码页面 ===")
    
    try:
        response = requests.get(f"{BASE_URL}/forgot-password")
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 忘记密码页面加载成功")
            return True
        else:
            print(f"❌ 忘记密码页面加载失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试邮箱验证码和密码重置功能...")
    print("=" * 50)
    
    # 测试忘记密码页面
    test_forgot_password_page()
    
    # 测试发送验证码
    if test_send_verification_code():
        print("\n请检查邮箱，然后继续测试...")
        time.sleep(2)
        
        # 测试密码重置
        if test_reset_password():
            # 测试新密码登录
            test_login_with_new_password()
    
    print("\n" + "=" * 50)
    print("=== 测试完成 ===")

if __name__ == "__main__":
    main()
