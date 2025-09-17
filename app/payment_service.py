"""
支付服务模块
支持微信支付和支付宝支付
"""
import os
import json
import time
import hashlib
import hmac
import base64
from datetime import datetime
from typing import Dict, Any, Optional
import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend

class WeChatPayService:
    """微信支付服务"""
    
    def __init__(self):
        # 微信支付配置
        self.app_id = os.getenv('WECHAT_APP_ID', '')
        self.mch_id = os.getenv('WECHAT_MCH_ID', '')
        self.api_key = os.getenv('WECHAT_API_KEY', '')
        self.cert_serial_no = os.getenv('WECHAT_CERT_SERIAL_NO', '')
        self.private_key_path = os.getenv('WECHAT_PRIVATE_KEY_PATH', '')
        self.cert_path = os.getenv('WECHAT_CERT_PATH', '')
        
        # API地址
        self.base_url = 'https://api.mch.weixin.qq.com'
        self.unified_order_url = f'{self.base_url}/v3/pay/transactions/jsapi'
        self.query_order_url = f'{self.base_url}/v3/pay/transactions/out-trade-no'
        self.close_order_url = f'{self.base_url}/v3/pay/transactions/out-trade-no'
        
    def create_jsapi_order(self, order_id: str, amount: int, description: str, 
                          openid: str, notify_url: str) -> Dict[str, Any]:
        """创建JSAPI支付订单"""
        try:
            # 构建请求数据
            data = {
                "appid": self.app_id,
                "mchid": self.mch_id,
                "description": description,
                "out_trade_no": order_id,
                "notify_url": notify_url,
                "amount": {
                    "total": amount,  # 金额，单位分
                    "currency": "CNY"
                },
                "payer": {
                    "openid": openid
                }
            }
            
            # 生成签名
            timestamp = str(int(time.time()))
            nonce_str = self._generate_nonce()
            method = 'POST'
            url_path = '/v3/pay/transactions/jsapi'
            body = json.dumps(data, separators=(',', ':'))
            
            # 构建签名字符串
            sign_str = f"{method}\n{url_path}\n{timestamp}\n{nonce_str}\n{body}\n"
            signature = self._generate_signature(sign_str)
            
            # 构建请求头
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'WECHATPAY2-SHA256-RSA2048 mchid="{self.mch_id}",nonce_str="{nonce_str}",signature="{signature}",timestamp="{timestamp}",serial_no="{self.cert_serial_no}"'
            }
            
            # 发送请求
            response = requests.post(
                self.unified_order_url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'prepay_id' in result:
                    # 生成前端调用的支付参数
                    pay_params = self._generate_jsapi_pay_params(result['prepay_id'])
                    return {
                        'success': True,
                        'prepay_id': result['prepay_id'],
                        'pay_params': pay_params
                    }
                else:
                    return {
                        'success': False,
                        'message': result.get('message', '创建订单失败')
                    }
            else:
                return {
                    'success': False,
                    'message': f'请求失败: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'创建微信支付订单失败: {str(e)}'
            }
    
    def query_order(self, order_id: str) -> Dict[str, Any]:
        """查询订单状态"""
        try:
            url = f"{self.query_order_url}/{order_id}?mchid={self.mch_id}"
            
            # 生成签名
            timestamp = str(int(time.time()))
            nonce_str = self._generate_nonce()
            method = 'GET'
            url_path = f'/v3/pay/transactions/out-trade-no/{order_id}'
            
            sign_str = f"{method}\n{url_path}\n{timestamp}\n{nonce_str}\n"
            signature = self._generate_signature(sign_str)
            
            headers = {
                'Accept': 'application/json',
                'Authorization': f'WECHATPAY2-SHA256-RSA2048 mchid="{self.mch_id}",nonce_str="{nonce_str}",signature="{signature}",timestamp="{timestamp}",serial_no="{self.cert_serial_no}"'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'order_info': result
                }
            else:
                return {
                    'success': False,
                    'message': f'查询失败: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'查询订单失败: {str(e)}'
            }
    
    def _generate_nonce(self) -> str:
        """生成随机字符串"""
        import random
        import string
        return ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    
    def _generate_signature(self, sign_str: str) -> str:
        """生成签名"""
        try:
            # 读取私钥
            with open(self.private_key_path, 'rb') as f:
                private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )
            
            # 使用私钥签名
            signature = private_key.sign(
                sign_str.encode('utf-8'),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            
            # Base64编码
            return base64.b64encode(signature).decode('utf-8')
            
        except Exception as e:
            print(f"生成签名失败: {e}")
            return ""
    
    def _generate_jsapi_pay_params(self, prepay_id: str) -> Dict[str, str]:
        """生成JSAPI支付参数"""
        timestamp = str(int(time.time()))
        nonce_str = self._generate_nonce()
        package = f"prepay_id={prepay_id}"
        
        # 构建签名字符串
        sign_str = f"{self.app_id}\n{timestamp}\n{nonce_str}\n{package}\n"
        pay_sign = self._generate_signature(sign_str)
        
        return {
            'appId': self.app_id,
            'timeStamp': timestamp,
            'nonceStr': nonce_str,
            'package': package,
            'signType': 'RSA',
            'paySign': pay_sign
        }
    
    def verify_notify(self, headers: Dict[str, str], body: str) -> Dict[str, Any]:
        """验证支付通知"""
        try:
            # 验证签名
            timestamp = headers.get('Wechatpay-Timestamp', '')
            nonce = headers.get('Wechatpay-Nonce', '')
            signature = headers.get('Wechatpay-Signature', '')
            serial = headers.get('Wechatpay-Serial', '')
            
            # 构建验签字符串
            sign_str = f"{timestamp}\n{nonce}\n{body}\n"
            
            # 验证签名（这里需要实现签名验证逻辑）
            # 实际项目中需要根据微信支付文档实现
            
            # 解析通知数据
            notify_data = json.loads(body)
            
            return {
                'success': True,
                'data': notify_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'验证通知失败: {str(e)}'
            }


class AlipayService:
    """支付宝支付服务"""
    
    def __init__(self):
        # 支付宝配置
        self.app_id = os.getenv('ALIPAY_APP_ID', '')
        self.private_key_path = os.getenv('ALIPAY_PRIVATE_KEY_PATH', '')
        self.alipay_public_key_path = os.getenv('ALIPAY_PUBLIC_KEY_PATH', '')
        self.notify_url = os.getenv('ALIPAY_NOTIFY_URL', '')
        self.return_url = os.getenv('ALIPAY_RETURN_URL', '')
        
        # 环境配置
        self.sandbox = os.getenv('ALIPAY_SANDBOX', 'true').lower() == 'true'
        self.base_url = 'https://openapi.alipaydev.com/gateway.do' if self.sandbox else 'https://openapi.alipay.com/gateway.do'
    
    def create_app_pay_order(self, order_id: str, amount: float, subject: str) -> Dict[str, Any]:
        """创建APP支付订单"""
        try:
            from alipay import AliPay
            
            # 初始化支付宝客户端
            alipay = AliPay(
                appid=self.app_id,
                app_notify_url=self.notify_url,
                app_private_key_path=self.private_key_path,
                alipay_public_key_path=self.alipay_public_key_path,
                sign_type="RSA2",
                debug=self.sandbox
            )
            
            # 构建订单参数
            order_string = alipay.api_alipay_trade_app_pay(
                out_trade_no=order_id,
                total_amount=amount,
                subject=subject,
                notify_url=self.notify_url
            )
            
            return {
                'success': True,
                'order_string': order_string
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'创建支付宝订单失败: {str(e)}'
            }
    
    def create_web_pay_order(self, order_id: str, amount: float, subject: str) -> Dict[str, Any]:
        """创建网页支付订单"""
        try:
            from alipay import AliPay
            
            # 初始化支付宝客户端
            alipay = AliPay(
                appid=self.app_id,
                app_notify_url=self.notify_url,
                app_private_key_path=self.private_key_path,
                alipay_public_key_path=self.alipay_public_key_path,
                sign_type="RSA2",
                debug=self.sandbox
            )
            
            # 构建订单参数
            order_string = alipay.api_alipay_trade_page_pay(
                out_trade_no=order_id,
                total_amount=amount,
                subject=subject,
                return_url=self.return_url,
                notify_url=self.notify_url
            )
            
            # 生成支付URL
            pay_url = f"{self.base_url}?{order_string}"
            
            return {
                'success': True,
                'pay_url': pay_url,
                'order_string': order_string
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'创建支付宝订单失败: {str(e)}'
            }
    
    def query_order(self, order_id: str) -> Dict[str, Any]:
        """查询订单状态"""
        try:
            from alipay import AliPay
            
            alipay = AliPay(
                appid=self.app_id,
                app_notify_url=self.notify_url,
                app_private_key_path=self.private_key_path,
                alipay_public_key_path=self.alipay_public_key_path,
                sign_type="RSA2",
                debug=self.sandbox
            )
            
            result = alipay.api_alipay_trade_query(out_trade_no=order_id)
            
            return {
                'success': True,
                'order_info': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'查询订单失败: {str(e)}'
            }
    
    def verify_notify(self, data: Dict[str, str]) -> Dict[str, Any]:
        """验证支付通知"""
        try:
            from alipay import AliPay
            
            alipay = AliPay(
                appid=self.app_id,
                app_notify_url=self.notify_url,
                app_private_key_path=self.private_key_path,
                alipay_public_key_path=self.alipay_public_key_path,
                sign_type="RSA2",
                debug=self.sandbox
            )
            
            # 验证签名
            success = alipay.verify(data, data.get('sign'))
            
            if success:
                return {
                    'success': True,
                    'data': data
                }
            else:
                return {
                    'success': False,
                    'message': '签名验证失败'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'验证通知失败: {str(e)}'
            }


class PaymentService:
    """统一支付服务"""
    
    def __init__(self):
        self.wechat_pay = WeChatPayService()
        self.alipay = AlipayService()
    
    def create_payment_order(self, payment_method: str, order_id: str, amount: float, 
                           description: str, **kwargs) -> Dict[str, Any]:
        """创建支付订单"""
        try:
            # 转换金额单位（微信支付需要分）
            if payment_method == 'wechat':
                amount_cents = int(amount * 100)
                openid = kwargs.get('openid', '')
                notify_url = kwargs.get('notify_url', '')
                
                if not openid:
                    return {'success': False, 'message': '微信支付需要openid'}
                
                return self.wechat_pay.create_jsapi_order(
                    order_id=order_id,
                    amount=amount_cents,
                    description=description,
                    openid=openid,
                    notify_url=notify_url
                )
            
            elif payment_method == 'alipay':
                subject = kwargs.get('subject', description)
                
                return self.alipay.create_web_pay_order(
                    order_id=order_id,
                    amount=amount,
                    subject=subject
                )
            
            else:
                return {'success': False, 'message': '不支持的支付方式'}
                
        except Exception as e:
            return {'success': False, 'message': f'创建支付订单失败: {str(e)}'}
    
    def query_payment_order(self, payment_method: str, order_id: str) -> Dict[str, Any]:
        """查询支付订单"""
        try:
            if payment_method == 'wechat':
                return self.wechat_pay.query_order(order_id)
            elif payment_method == 'alipay':
                return self.alipay.query_order(order_id)
            else:
                return {'success': False, 'message': '不支持的支付方式'}
                
        except Exception as e:
            return {'success': False, 'message': f'查询订单失败: {str(e)}'}
    
    def verify_payment_notify(self, payment_method: str, **kwargs) -> Dict[str, Any]:
        """验证支付通知"""
        try:
            if payment_method == 'wechat':
                headers = kwargs.get('headers', {})
                body = kwargs.get('body', '')
                return self.wechat_pay.verify_notify(headers, body)
            
            elif payment_method == 'alipay':
                data = kwargs.get('data', {})
                return self.alipay.verify_notify(data)
            
            else:
                return {'success': False, 'message': '不支持的支付方式'}
                
        except Exception as e:
            return {'success': False, 'message': f'验证通知失败: {str(e)}'}
