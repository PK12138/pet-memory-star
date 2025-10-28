# 批量更新小程序主题配色为深色星空主题
# 将紫色渐变替换为深色星空主题

$files = Get-ChildItem -Path "pages" -Filter "*.wxss" -Recurse

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    
    # 替换紫色渐变背景为深色星空
    $content = $content -replace 'background:\s*linear-gradient\(135deg,\s*#667eea\s+0%,\s*#764ba2\s+50%,\s*#f093fb\s+100%\)', 'background: radial-gradient(ellipse at bottom, #1b2735 0%, #090a0f 100%)'
    
    # 替换其他紫色渐变
    $content = $content -replace 'linear-gradient\(135deg,\s*#667eea\s+0%,\s*#764ba2\s+100%\)', 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)'
    
    # 替换按钮渐变
    $content = $content -replace 'background:\s*linear-gradient\(135deg,\s*#667eea\s+0%,\s*#764ba2\s+50%,\s*#f093fb\s+100%\);', 'background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);'
    
    # 保存文件
    Set-Content -Path $file.FullName -Value $content -Encoding UTF8 -NoNewline
    
    Write-Host "已更新: $($file.FullName)"
}

Write-Host "`n主题更新完成！" -ForegroundColor Green

