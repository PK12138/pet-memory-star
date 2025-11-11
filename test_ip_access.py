#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试IP地址访问
比较域名和IP访问的差异
"""
import sys
import io
import requests
import json

# 设置Windows控制台输出编码为UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_access():
    print("🧪 测试IP地址访问")
    print("=" * 60)
    
    # 测试地址列表
    test_urls = [
        {
            'name': 'IP地址（无端口）',
            'base': 'http://42.193.230.145',
            'endpoints': ['/api/health', '/api/auth/login', '/docs']
        },
        {
            'name': 'IP地址（带8000端口）',
            'base': 'http://42.193.230.145:8000',
            'endpoints': ['/api/health', '/api/auth/login', '/docs']
        },
        {
            'name': '域名（无端口）',
            'base': 'http://pettrailstar.cn',
            'endpoints': ['/api/health', '/api/auth/login', '/docs']
        }
    ]
    
    results = {}
    
    for test_group in test_urls:
        print(f"\n📡 测试: {test_group['name']}")
        print(f"基础URL: {test_group['base']}")
        print("-" * 60)
        
        results[test_group['name']] = {}
        
        for endpoint in test_group['endpoints']:
            url = test_group['base'] + endpoint
            try:
                response = requests.get(url, timeout=5)
                status = "✅" if response.status_code == 200 else "⚠️"
                print(f"  {status} {endpoint}: {response.status_code}")
                
                results[test_group['name']][endpoint] = {
                    'success': response.status_code == 200,
                    'status_code': response.status_code
                }
                
                # 如果是健康检查，显示响应内容
                if endpoint == '/api/health':
                    try:
                        # 尝试解析JSON
                        data = response.json()
                        print(f"      响应: {json.dumps(data, ensure_ascii=False)}")
                    except:
                        # 如果不是JSON，显示前100个字符
                        content = response.text[:100].replace('\n', ' ')
                        print(f"      响应: {content}...")
                        
            except requests.exceptions.Timeout:
                print(f"  ❌ {endpoint}: 连接超时")
                results[test_group['name']][endpoint] = {
                    'success': False,
                    'error': 'timeout'
                }
            except requests.exceptions.ConnectionError:
                print(f"  ❌ {endpoint}: 连接失败")
                results[test_group['name']][endpoint] = {
                    'success': False,
                    'error': 'connection_error'
                }
            except Exception as e:
                print(f"  ❌ {endpoint}: {str(e)[:50]}")
                results[test_group['name']][endpoint] = {
                    'success': False,
                    'error': str(e)[:50]
                }
    
    # 测试登录接口
    print(f"\n🔐 测试登录接口")
    print("-" * 60)
    
    for test_group in test_urls:
        url = test_group['base'] + '/api/auth/login'
        try:
            response = requests.post(
                url,
                json={'email': 'test@example.com', 'password': 'test123'},
                timeout=5
            )
            status = "✅" if response.status_code == 200 else "⚠️"
            print(f"{status} {test_group['name']}: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"    响应: {json.dumps(data, ensure_ascii=False)[:100]}")
                except:
                    pass
        except requests.exceptions.Timeout:
            print(f"❌ {test_group['name']}: 超时")
        except Exception as e:
            print(f"❌ {test_group['name']}: {str(e)[:50]}")
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    
    for name, endpoints in results.items():
        success_count = sum(1 for e in endpoints.values() if e.get('success'))
        total = len(endpoints)
        status = "✅" if success_count == total else "❌"
        print(f"{status} {name}: {success_count}/{total} 个接口可用")
    
    print("\n💡 建议:")
    
    # 找出最佳配置
    best_config = None
    for name, endpoints in results.items():
        if all(e.get('success') for e in endpoints.values()):
            best_config = name
            break
    
    if best_config:
        base_url = next(t['base'] for t in test_urls if t['name'] == best_config)
        print(f"✅ 推荐配置: {best_config}")
        print(f"   baseUrl: '{base_url}'")
        print(f"\n   在 miniprogram/utils/api.js 和 miniprogram/app.js 中设置:")
        print(f"   const config = {{ baseUrl: '{base_url}' }}")
    else:
        print("❌ 所有配置都有问题，请检查服务器配置")
        print("   可能的原因:")
        print("   1. 防火墙阻止了某些端口")
        print("   2. Nginx配置不正确")
        print("   3. 域名解析问题")

if __name__ == "__main__":
    test_access()


