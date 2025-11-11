#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证小程序配置脚本
检查配置是否正确指向服务器
"""

import os
import re

def check_config():
    print("🔍 验证小程序配置...")
    print("=" * 50)
    
    # 检查 app.js
    app_js_path = "miniprogram/app.js"
    if os.path.exists(app_js_path):
        with open(app_js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("📄 检查 app.js:")
        
        # 检查是否包含正确的 baseUrl
        if "baseUrl: 'http://pettrailstar.cn'" in content:
            print("✅ baseUrl 配置正确: http://pettrailstar.cn")
        elif "baseUrl: 'http://localhost:8000'" in content:
            print("❌ baseUrl 配置错误: http://localhost:8000")
        else:
            print("⚠️  无法确定 baseUrl 配置")
        
        # 检查是否包含调试输出
        if "console.log('=== 小程序配置信息 ===')" in content:
            print("✅ 包含调试输出，便于排查问题")
        else:
            print("⚠️  缺少调试输出")
            
        # 检查 AppID
        if "appId: 'wx9572f66945407446'" in content:
            print("✅ AppID 配置正确")
        else:
            print("❌ AppID 配置错误")
    else:
        print("❌ 找不到 app.js 文件")
    
    print()
    
    # 检查 config.js
    config_js_path = "miniprogram/config/config.js"
    if os.path.exists(config_js_path):
        with open(config_js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("📄 检查 config.js:")
        
        if "baseUrl: 'http://pettrailstar.cn'" in content:
            print("✅ baseUrl 配置正确: http://pettrailstar.cn")
        else:
            print("❌ baseUrl 配置错误")
    else:
        print("❌ 找不到 config.js 文件")
    
    print()
    
    # 检查 config-local.js
    config_local_path = "miniprogram/config/config-local.js"
    if os.path.exists(config_local_path):
        with open(config_local_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("📄 检查 config-local.js:")
        
        if "baseUrl: 'http://localhost:8000'" in content:
            print("✅ 本地配置正确: http://localhost:8000")
        else:
            print("❌ 本地配置错误")
    else:
        print("❌ 找不到 config-local.js 文件")
    
    print()
    print("=" * 50)
    print("📱 下一步操作:")
    print("1. 在微信开发者工具中点击'编译'")
    print("2. 查看 Console 面板，应该显示:")
    print("   === 小程序配置信息 ===")
    print("   baseUrl: http://pettrailstar.cn")
    print("   appId: wx9572f66945407446")
    print("   ========================")
    print("3. 如果仍显示 localhost:8000，请:")
    print("   - 清除微信开发者工具缓存")
    print("   - 重新编译")
    print("   - 或重启微信开发者工具")

if __name__ == "__main__":
    check_config()

