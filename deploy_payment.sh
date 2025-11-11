#!/bin/bash

# 支付功能一键部署脚本
# 用于在云端服务器部署支付功能

echo "🚀 开始部署支付功能..."

# 检查是否在正确的目录
if [ ! -f "app/main.py" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

# 1. 安装支付依赖
echo "📦 安装支付依赖..."
pip install -r requirements_payment.txt

# 2. 创建证书目录
echo "📁 创建证书目录..."
mkdir -p certs
chmod 700 certs

# 3. 检查环境变量
echo "🔧 检查环境变量..."
if [ -z "$WECHAT_APP_ID" ]; then
    echo "⚠️  警告: WECHAT_APP_ID 未设置"
fi

if [ -z "$ALIPAY_APP_ID" ]; then
    echo "⚠️  警告: ALIPAY_APP_ID 未设置"
fi

# 4. 检查证书文件
echo "🔐 检查证书文件..."
cert_files=(
    "certs/wechat_private_key.pem"
    "certs/wechat_cert.pem"
    "certs/alipay_private_key.pem"
    "certs/alipay_public_key.pem"
)

for cert_file in "${cert_files[@]}"; do
    if [ ! -f "$cert_file" ]; then
        echo "⚠️  警告: $cert_file 不存在"
    else
        echo "✅ $cert_file 存在"
    fi
done

# 5. 设置证书权限
echo "🔒 设置证书权限..."
chmod 600 certs/*.pem 2>/dev/null || true

# 6. 测试支付服务
echo "🧪 测试支付服务..."
python test_payment.py

# 7. 重启服务
echo "🔄 重启服务..."
pkill -f "start_server.py" || true
sleep 2

# 启动服务
nohup python3 start_server.py > app.log 2>&1 &
echo "✅ 服务已启动"

# 8. 检查服务状态
echo "📊 检查服务状态..."
sleep 5

if pgrep -f "start_server.py" > /dev/null; then
    echo "✅ 服务运行正常"
    
    # 测试API端点
    echo "🌐 测试API端点..."
    curl -s http://localhost:8000/api/payment/plans > /dev/null
    if [ $? -eq 0 ]; then
        echo "✅ 支付API正常"
    else
        echo "❌ 支付API异常"
    fi
else
    echo "❌ 服务启动失败"
    echo "查看日志: tail -f app.log"
fi

echo ""
echo "🎉 支付功能部署完成！"
echo ""
echo "📋 后续步骤:"
echo "1. 配置支付平台证书"
echo "2. 设置环境变量"
echo "3. 测试支付功能"
echo "4. 配置HTTPS（生产环境必需）"
echo ""
echo "📖 详细说明请查看: PAYMENT_SETUP.md"
