#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试服务器连接
用于验证线上服务器是否正常运行
"""
import sys
import io
import requests
import json
from datetime import datetime

# 设置Windows控制台输出编码为UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 服务器配置
SERVER_IP = "42.193.230.145"
SERVER_PORT = 8000
SERVER_DOMAIN = "pettrailstar.cn"

def test_server_connection():
    """测试服务器连接"""
    print("🚀 爪迹星服务器连接测试")
    print("=" * 60)
    print(f"服务器IP: {SERVER_IP}")
    print(f"服务器端口: {SERVER_PORT}")
    print(f"域名: {SERVER_DOMAIN}")
    print("=" * 60)
    print()
    
    # 测试地址列表
    test_urls = [
        {
            'name': 'HTTP - IP地址',
            'url': f'http://{SERVER_IP}:{SERVER_PORT}',
            'endpoints': [
                '/api/health',
                '/docs',
                '/api/auth/login'
            ]
        },
        {
            'name': 'HTTPS - 域名',
            'url': f'https://{SERVER_DOMAIN}',
            'endpoints': [
                '/api/health',
                '/docs'
            ]
        },
        {
            'name': 'HTTP - 域名',
            'url': f'http://{SERVER_DOMAIN}',
            'endpoints': [
                '/api/health',
                '/docs'
            ]
        }
    ]
    
    results = []
    
    for test_group in test_urls:
        print(f"\n📡 测试 {test_group['name']}")
        print(f"基础URL: {test_group['url']}")
        print("-" * 60)
        
        for endpoint in test_group['endpoints']:
            full_url = test_group['url'] + endpoint
            try:
                response = requests.get(full_url, timeout=5)
                status = "✅" if response.status_code == 200 else "⚠️"
                result = {
                    'url': full_url,
                    'status_code': response.status_code,
                    'success': response.status_code == 200
                }
                print(f"  {status} {endpoint}: {response.status_code}")
                
                # 如果是健康检查接口，显示响应内容
                if endpoint == '/api/health' and response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"      响应: {json.dumps(data, ensure_ascii=False)}")
                    except:
                        pass
                        
            except requests.exceptions.Timeout:
                print(f"  ❌ {endpoint}: 连接超时")
                result = {'url': full_url, 'error': '超时'}
            except requests.exceptions.ConnectionError as e:
                print(f"  ❌ {endpoint}: 连接失败")
                result = {'url': full_url, 'error': '连接失败'}
            except Exception as e:
                print(f"  ❌ {endpoint}: {str(e)}")
                result = {'url': full_url, 'error': str(e)}
            
            results.append(result)
    
    # 测试登录接口
    print("\n🔐 测试登录接口")
    print("-" * 60)
    
    login_url = f'http://{SERVER_IP}:{SERVER_PORT}/api/auth/login'
    test_data = {
        'username': 'test_user',
        'password': 'test_password'
    }
    
    try:
        response = requests.post(login_url, json=test_data, timeout=5)
        print(f"  状态码: {response.status_code}")
        print(f"  响应: {response.text[:200]}")
    except Exception as e:
        print(f"  ❌ 登录接口测试失败: {str(e)}")
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    
    successful = sum(1 for r in results if r.get('success', False))
    total = len(results)
    
    print(f"成功: {successful}/{total}")
    
    if successful > 0:
        print("\n✅ 建议使用的配置:")
        # 找出第一个成功的URL
        for test_group in test_urls:
            for endpoint in test_group['endpoints']:
                full_url = test_group['url'] + endpoint
                if any(r.get('url') == full_url and r.get('success') for r in results):
                    print(f"   baseUrl: '{test_group['url']}'")
                    print(f"\n   在 miniprogram/config/config.js 中设置:")
                    print(f"   baseUrl: '{test_group['url']}'")
                    return
    else:
        print("\n❌ 所有测试均失败")
        print("\n可能的原因:")
        print("  1. 服务器未启动")
        print("  2. 防火墙阻止了连接")
        print("  3. 端口配置不正确")
        print("  4. 网络连接问题")
        print("\n建议:")
        print("  1. 在服务器上运行: systemctl status pet-memory-star")
        print("  2. 检查防火墙: sudo ufw status")
        print("  3. 检查端口监听: netstat -tlnp | grep 8000")

if __name__ == "__main__":
    test_server_connection()

