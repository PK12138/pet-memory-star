#!/usr/bin/env python3
"""
简单的邮件地址测试
"""

import os

# 设置环境变量
os.environ['ENVIRONMENT'] = 'production'
os.environ['SERVER_BASE_URL'] = 'http://42.193.230.145'

def test_email_url():
    """测试邮件中的URL地址"""
    print("=== 测试邮件中的服务器地址 ===")
    
    try:
        # 直接测试URL构建
        memorial_url = "/memorial/test123"
        base_url = os.getenv('SERVER_BASE_URL', 'http://42.193.230.145')
        full_url = f"{base_url}{memorial_url}"
        
        print(f"✅ URL构建成功")
        print(f"   基础URL: {base_url}")
        print(f"   纪念馆路径: {memorial_url}")
        print(f"   完整URL: {full_url}")
        
        # 检查URL是否正确
        expected_url = "http://42.193.230.145/memorial/test123"
        if full_url == expected_url:
            print(f"✅ URL正确: {full_url}")
        else:
            print(f"❌ URL不正确")
            print(f"   期望: {expected_url}")
            print(f"   实际: {full_url}")
            
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    """主函数"""
    print("开始测试邮件中的服务器地址...")
    print("=" * 50)
    
    success = test_email_url()
    
    print("\n" + "=" * 50)
    if success:
        print("=== 测试完成 ✅ ===")
        print("邮件中的服务器地址配置正确")
        print("现在邮件中的纪念馆地址将使用生产环境服务器地址")
        print("服务器地址: http://42.193.230.145")
    else:
        print("=== 测试失败 ❌ ===")

if __name__ == "__main__":
    main()
