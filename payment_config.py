"""
支付配置文件
请根据实际情况修改配置
"""
import os

# 微信支付配置
WECHAT_PAY_CONFIG = {
    # 应用ID
    'app_id': os.getenv('WECHAT_APP_ID', 'your_wechat_app_id'),
    
    # 商户号
    'mch_id': os.getenv('WECHAT_MCH_ID', 'your_merchant_id'),
    
    # API密钥
    'api_key': os.getenv('WECHAT_API_KEY', 'your_api_key'),
    
    # 证书序列号
    'cert_serial_no': os.getenv('WECHAT_CERT_SERIAL_NO', 'your_cert_serial_no'),
    
    # 私钥文件路径
    'private_key_path': os.getenv('WECHAT_PRIVATE_KEY_PATH', 'certs/wechat_private_key.pem'),
    
    # 证书文件路径
    'cert_path': os.getenv('WECHAT_CERT_PATH', 'certs/wechat_cert.pem'),
    
    # 支付回调地址
    'notify_url': os.getenv('WECHAT_NOTIFY_URL', 'https://yourdomain.com/api/payment/wechat/notify'),
}

# 支付宝配置
ALIPAY_CONFIG = {
    # 应用ID
    'app_id': os.getenv('ALIPAY_APP_ID', 'your_alipay_app_id'),
    
    # 私钥文件路径
    'private_key_path': os.getenv('ALIPAY_PRIVATE_KEY_PATH', 'certs/alipay_private_key.pem'),
    
    # 支付宝公钥文件路径
    'alipay_public_key_path': os.getenv('ALIPAY_PUBLIC_KEY_PATH', 'certs/alipay_public_key.pem'),
    
    # 支付回调地址
    'notify_url': os.getenv('ALIPAY_NOTIFY_URL', 'https://yourdomain.com/api/payment/alipay/notify'),
    
    # 支付返回地址
    'return_url': os.getenv('ALIPAY_RETURN_URL', 'https://yourdomain.com/payment/success'),
    
    # 是否沙箱环境
    'sandbox': os.getenv('ALIPAY_SANDBOX', 'true').lower() == 'true',
}

# 支付方式配置
PAYMENT_METHODS = {
    'wechat': {
        'name': '微信支付',
        'icon': '💚',
        'enabled': True,
        'config': WECHAT_PAY_CONFIG
    },
    'alipay': {
        'name': '支付宝',
        'icon': '🔵',
        'enabled': True,
        'config': ALIPAY_CONFIG
    }
}

# 套餐配置
PAYMENT_PLANS = {
    'monthly': {
        'id': 'monthly',
        'name': '月度会员',
        'price': 29.9,
        'period': '1个月',
        'features': [
            '无限纪念馆',
            '无限照片上传',
            'AI智能功能',
            '数据导出',
            '优先客服支持'
        ],
        'recommended': False
    },
    'yearly': {
        'id': 'yearly',
        'name': '年度会员',
        'price': 299.0,
        'period': '12个月',
        'features': [
            '无限纪念馆',
            '无限照片上传',
            'AI智能功能',
            '数据导出',
            '优先客服支持',
            '专属主题',
            '自定义域名'
        ],
        'recommended': True
    }
}
