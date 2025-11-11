#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试登录API
诊断小程序登录失败的具体原因
"""
import requests
import json
import sys
import io

# 设置Windows控制台输出编码为UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_login_api():
    """测试登录API"""
    print("🔐 测试登录API")
    print("=" * 50)
    
    base_url = "http://pettrailstar.cn"
    login_url = f"{base_url}/api/auth/login"
    
    # 测试数据
    test_cases = [
        {
            'name': '正确格式的登录请求',
            'data': {
                'email': 'test@example.com',
                'password': 'test123'
            }
        },
        {
            'name': '空数据请求',
            'data': {}
        },
        {
            'name': '只有邮箱的请求',
            'data': {
                'email': 'test@example.com'
            }
        },
        {
            'name': '只有密码的请求',
            'data': {
                'password': 'test123'
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 测试 {i}: {test_case['name']}")
        print(f"请求URL: {login_url}")
        print(f"请求数据: {json.dumps(test_case['data'], ensure_ascii=False)}")
        print("-" * 40)
        
        try:
            response = requests.post(
                login_url,
                json=test_case['data'],
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                },
                timeout=10
            )
            
            print(f"状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            
            try:
                response_data = response.json()
                print(f"响应数据: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
            except:
                print(f"响应文本: {response.text[:200]}")
            
            if response.status_code == 200:
                print("✅ 请求成功")
            elif response.status_code == 400:
                print("⚠️  请求参数错误（这是正常的，因为我们用的是测试数据）")
            elif response.status_code == 401:
                print("⚠️  认证失败（这是正常的，因为我们用的是测试数据）")
            else:
                print(f"❌ 请求失败: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("❌ 请求超时")
        except requests.exceptions.ConnectionError as e:
            print(f"❌ 连接错误: {e}")
        except Exception as e:
            print(f"❌ 其他错误: {e}")
    
    # 测试服务器健康状态
    print(f"\n🏥 测试服务器健康状态")
    print("-" * 40)
    
    health_url = f"{base_url}/api/health"
    try:
        response = requests.get(health_url, timeout=5)
        print(f"健康检查状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ 服务器运行正常")
            try:
                health_data = response.json()
                print(f"健康检查数据: {json.dumps(health_data, ensure_ascii=False, indent=2)}")
            except:
                print(f"健康检查响应: {response.text}")
        else:
            print("❌ 服务器健康检查失败")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
    
    # 测试API文档
    print(f"\n📚 测试API文档")
    print("-" * 40)
    
    docs_url = f"{base_url}/docs"
    try:
        response = requests.get(docs_url, timeout=5)
        print(f"API文档状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ API文档可访问")
        else:
            print("❌ API文档不可访问")
    except Exception as e:
        print(f"❌ API文档访问失败: {e}")
    
    print("\n" + "=" * 50)
    print("📊 诊断总结")
    print("=" * 50)
    print("如果所有测试都显示连接正常，但小程序仍然失败，可能的原因：")
    print("1. 小程序请求头格式问题")
    print("2. 小程序网络权限问题")
    print("3. 微信开发者工具缓存问题")
    print("4. 服务器CORS配置问题")
    print("\n建议下一步：")
    print("1. 在微信开发者工具中查看Network面板的详细请求")
    print("2. 检查请求头是否正确")
    print("3. 清除微信开发者工具缓存")
    print("4. 检查服务器日志")

if __name__ == "__main__":
    test_login_api()
