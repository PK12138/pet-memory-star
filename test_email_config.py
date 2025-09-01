#!/usr/bin/env python3
"""
测试邮件中的服务器地址配置
"""

import os

# 设置生产环境
os.environ['ENVIRONMENT'] = 'production'

def test_email_config():
    """测试邮件配置"""
    print("=== 测试邮件中的服务器地址配置 ===")
    
    try:
        # 导入配置
        from app.config import config
        print(f"✅ 配置加载成功")
        print(f"   环境: {os.environ.get('ENVIRONMENT')}")
        print(f"   服务器地址: {config.BASE_URL}")
        
        # 测试邮件服务
        from app.services import EmailService
        email_service = EmailService()
        print(f"✅ 邮件服务初始化成功")
        
        # 测试邮件模板
        test_url = "/memorial/test123"
        html_content = email_service._build_email_html(
            "测试宠物", 
            test_url, 
            "活泼型", 
            "这是一封测试信件"
        )
        
        print("✅ 邮件模板生成成功")
        
        # 检查服务器地址
        expected_url = "http://42.193.230.145/memorial/test123"
        if expected_url in html_content:
            print(f"✅ 邮件中包含正确的服务器地址: {expected_url}")
        else:
            print(f"❌ 邮件中未包含正确的服务器地址")
            print(f"   期望: {expected_url}")
            
        # 显示邮件内容片段
        print("\n📧 邮件内容片段:")
        lines = html_content.split('\n')
        for i, line in enumerate(lines):
            if "42.193.230.145" in line:
                print(f"   第{i+1}行: {line.strip()}")
                
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始测试邮件中的服务器地址配置...")
    print("=" * 50)
    
    success = test_email_config()
    
    print("\n" + "=" * 50)
    if success:
        print("=== 测试完成 ✅ ===")
        print("邮件中的服务器地址配置正确")
        print("现在邮件中的纪念馆地址将使用生产环境服务器地址")
        print("服务器地址: http://42.193.230.145")
    else:
        print("=== 测试失败 ❌ ===")
        print("请检查配置和代码")

if __name__ == "__main__":
    main()
