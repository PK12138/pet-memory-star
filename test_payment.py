#!/usr/bin/env python3
"""
支付功能测试工具
用于测试微信支付和支付宝支付集成
"""
import os
import sys
import json
import requests
from datetime import datetime

# 添加app目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from payment_service import PaymentService

def test_wechat_pay():
    """测试微信支付"""
    print("🧪 测试微信支付...")
    
    payment_service = PaymentService()
    
    # 测试创建订单
    order_id = f"test_wechat_{int(datetime.now().timestamp())}"
    amount = 0.01  # 测试金额1分
    description = "测试订单"
    openid = "test_openid_123"
    notify_url = "https://yourdomain.com/api/payment/wechat/notify"
    
    result = payment_service.create_payment_order(
        payment_method='wechat',
        order_id=order_id,
        amount=amount,
        description=description,
        openid=openid,
        notify_url=notify_url
    )
    
    print(f"创建订单结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if result['success']:
        print("✅ 微信支付订单创建成功")
    else:
        print(f"❌ 微信支付订单创建失败: {result['message']}")

def test_alipay():
    """测试支付宝支付"""
    print("🧪 测试支付宝支付...")
    
    payment_service = PaymentService()
    
    # 测试创建订单
    order_id = f"test_alipay_{int(datetime.now().timestamp())}"
    amount = 0.01  # 测试金额1分
    description = "测试订单"
    
    result = payment_service.create_payment_order(
        payment_method='alipay',
        order_id=order_id,
        amount=amount,
        description=description,
        subject=description
    )
    
    print(f"创建订单结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if result['success']:
        print("✅ 支付宝订单创建成功")
    else:
        print(f"❌ 支付宝订单创建失败: {result['message']}")

def test_payment_config():
    """测试支付配置"""
    print("🔧 检查支付配置...")
    
    # 检查环境变量
    wechat_vars = [
        'WECHAT_APP_ID',
        'WECHAT_MCH_ID', 
        'WECHAT_API_KEY',
        'WECHAT_CERT_SERIAL_NO',
        'WECHAT_PRIVATE_KEY_PATH',
        'WECHAT_CERT_PATH'
    ]
    
    alipay_vars = [
        'ALIPAY_APP_ID',
        'ALIPAY_PRIVATE_KEY_PATH',
        'ALIPAY_PUBLIC_KEY_PATH'
    ]
    
    print("微信支付配置:")
    for var in wechat_vars:
        value = os.getenv(var, '')
        status = "✅" if value else "❌"
        print(f"  {status} {var}: {'已设置' if value else '未设置'}")
    
    print("\n支付宝配置:")
    for var in alipay_vars:
        value = os.getenv(var, '')
        status = "✅" if value else "❌"
        print(f"  {status} {var}: {'已设置' if value else '未设置'}")
    
    # 检查证书文件
    print("\n证书文件检查:")
    cert_files = [
        'certs/wechat_private_key.pem',
        'certs/wechat_cert.pem',
        'certs/alipay_private_key.pem',
        'certs/alipay_public_key.pem'
    ]
    
    for cert_file in cert_files:
        exists = os.path.exists(cert_file)
        status = "✅" if exists else "❌"
        print(f"  {status} {cert_file}: {'存在' if exists else '不存在'}")

def test_api_endpoints():
    """测试API端点"""
    print("🌐 测试API端点...")
    
    base_url = "http://localhost:8000"
    endpoints = [
        "/api/payment/plans",
        "/payment",
        "/orders"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"  {status} {endpoint}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"  ❌ {endpoint}: 连接失败 - {e}")

def main():
    """主函数"""
    print("🚀 支付功能测试工具")
    print("=" * 50)
    
    # 检查配置
    test_payment_config()
    print()
    
    # 测试API端点
    test_api_endpoints()
    print()
    
    # 测试支付服务
    try:
        test_wechat_pay()
        print()
        test_alipay()
    except Exception as e:
        print(f"❌ 支付服务测试失败: {e}")
    
    print("\n" + "=" * 50)
    print("测试完成！")

if __name__ == "__main__":
    main()
