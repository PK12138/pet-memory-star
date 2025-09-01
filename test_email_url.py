#!/usr/bin/env python3
"""
测试邮件中的服务器地址
"""

import os

# 设置生产环境
os.environ['ENVIRONMENT'] = 'production'

def test_email_url():
    """测试邮件中的URL地址"""
    print("=== 测试邮件中的服务器地址 ===")
    
    try:
        from app.services import EmailService
        
        email_service = EmailService()
        
        # 测试邮件模板
        test_url = "/memorial/test123"
        html_content = email_service._build_email_html(
            "测试宠物", 
            test_url, 
            "活泼型", 
            "这是一封测试信件"
        )
        
        print("✅ 邮件模板生成成功")
        
        # 检查是否包含正确的服务器地址
        if "http://42.193.230.145" in html_content:
            print("✅ 邮件中包含正确的服务器地址")
            print(f"   服务器地址: http://42.193.230.145")
        else:
            print("❌ 邮件中未包含正确的服务器地址")
            
        # 检查完整的纪念馆URL
        expected_url = "http://42.193.230.145/memorial/test123"
        if expected_url in html_content:
            print(f"✅ 纪念馆URL正确: {expected_url}")
        else:
            print(f"❌ 纪念馆URL不正确，期望: {expected_url}")
            
        # 显示邮件内容片段
        print("\n📧 邮件内容片段:")
        lines = html_content.split('\n')
        for i, line in enumerate(lines):
            if "42.193.230.145" in line:
                print(f"   第{i+1}行: {line.strip()}")
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def main():
    """主函数"""
    print("开始测试邮件中的服务器地址...")
    print("=" * 50)
    
    test_email_url()
    
    print("\n" + "=" * 50)
    print("=== 测试完成 ===")

if __name__ == "__main__":
    main()
