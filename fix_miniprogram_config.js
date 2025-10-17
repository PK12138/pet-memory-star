#!/usr/bin/env node
/**
 * 修复小程序配置脚本
 * 确保小程序使用正确的服务器配置
 */

const fs = require('fs');
const path = require('path');

console.log('🔧 修复小程序配置...');

// 1. 检查 app.js 配置
const appJsPath = path.join(__dirname, 'miniprogram', 'app.js');
const appJsContent = fs.readFileSync(appJsPath, 'utf8');

console.log('📄 检查 app.js 配置:');
if (appJsContent.includes("require('./config/config')")) {
    console.log('✅ app.js 已配置使用生产环境 config');
} else {
    console.log('❌ app.js 配置错误');
}

// 2. 检查 config.js 配置
const configJsPath = path.join(__dirname, 'miniprogram', 'config', 'config.js');
const configJsContent = fs.readFileSync(configJsPath, 'utf8');

console.log('\n📄 检查 config.js 配置:');
const baseUrlMatch = configJsContent.match(/baseUrl:\s*['"`]([^'"`]+)['"`]/);
if (baseUrlMatch) {
    const baseUrl = baseUrlMatch[1];
    console.log(`baseUrl: ${baseUrl}`);
    
    if (baseUrl === 'http://pettrailstar.cn') {
        console.log('✅ baseUrl 配置正确');
    } else if (baseUrl === 'http://localhost:8000') {
        console.log('❌ baseUrl 配置错误：使用了本地地址');
        console.log('🔧 正在修复...');
        
        // 修复配置
        const fixedContent = configJsContent.replace(
            /baseUrl:\s*['"`]http:\/\/localhost:8000['"`]/,
            "baseUrl: 'http://pettrailstar.cn'"
        );
        
        fs.writeFileSync(configJsPath, fixedContent);
        console.log('✅ 已修复 baseUrl 配置');
    } else {
        console.log(`⚠️  baseUrl 配置异常: ${baseUrl}`);
    }
} else {
    console.log('❌ 无法找到 baseUrl 配置');
}

// 3. 检查 config-local.js 配置
const configLocalPath = path.join(__dirname, 'miniprogram', 'config', 'config-local.js');
const configLocalContent = fs.readFileSync(configLocalPath, 'utf8');

console.log('\n📄 检查 config-local.js 配置:');
const localBaseUrlMatch = configLocalContent.match(/baseUrl:\s*['"`]([^'"`]+)['"`]/);
if (localBaseUrlMatch) {
    console.log(`baseUrl: ${localBaseUrlMatch[1]}`);
    if (localBaseUrlMatch[1] === 'http://localhost:8000') {
        console.log('✅ 本地配置正确（用于开发调试）');
    }
}

// 4. 生成配置报告
console.log('\n📊 配置报告:');
console.log('=====================================');
console.log('生产环境配置:');
console.log('  - 文件: miniprogram/config/config.js');
console.log('  - baseUrl: http://pettrailstar.cn');
console.log('  - 用途: 线上小程序使用');
console.log('');
console.log('开发环境配置:');
console.log('  - 文件: miniprogram/config/config-local.js');
console.log('  - baseUrl: http://localhost:8000');
console.log('  - 用途: 本地开发调试');
console.log('');
console.log('当前 app.js 使用: 生产环境配置');
console.log('=====================================');

console.log('\n✅ 配置检查完成！');
console.log('\n📱 下一步操作:');
console.log('1. 在微信开发者工具中点击"编译"');
console.log('2. 查看 Console 面板，应该显示:');
console.log('   baseUrl: http://pettrailstar.cn');
console.log('3. 如果仍显示 localhost:8000，请清除缓存后重新编译');
