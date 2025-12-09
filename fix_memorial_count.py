#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复纪念馆数量统计问题
检查并清理 user_memorials 表中的无效记录
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'app', 'pet_memorials.db')

def check_and_fix_memorial_count():
    """检查并修复纪念馆数量统计"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 50)
    print("🔍 检查纪念馆数量统计问题")
    print("=" * 50)
    
    # 1. 检查所有用户及其纪念馆数量
    print("\n📊 用户纪念馆统计：")
    cursor.execute('''
    SELECT 
        u.id,
        u.email,
        u.nickname,
        COUNT(um.memorial_id) as memorial_count
    FROM users u
    LEFT JOIN user_memorials um ON u.id = um.user_id
    GROUP BY u.id
    ORDER BY memorial_count DESC
    ''')
    
    users = cursor.fetchall()
    for user_id, email, nickname, count in users:
        print(f"  用户 {user_id} ({email or nickname or '未命名'}): {count} 个纪念馆")
    
    # 2. 检查无效的 user_memorials 记录（纪念馆已不存在）
    print("\n🔍 检查无效的 user_memorials 记录...")
    cursor.execute('''
    SELECT um.user_id, um.memorial_id
    FROM user_memorials um
    LEFT JOIN memorials m ON um.memorial_id = m.id
    WHERE m.id IS NULL
    ''')
    
    invalid_records = cursor.fetchall()
    if invalid_records:
        print(f"  ⚠️  发现 {len(invalid_records)} 条无效记录：")
        for user_id, memorial_id in invalid_records:
            print(f"    用户 {user_id} - 纪念馆 {memorial_id} (纪念馆已不存在)")
        
        # 清理无效记录
        print("\n🧹 清理无效记录...")
        cursor.execute('''
        DELETE FROM user_memorials
        WHERE memorial_id NOT IN (SELECT id FROM memorials)
        ''')
        deleted_count = cursor.rowcount
        conn.commit()
        print(f"  ✅ 已删除 {deleted_count} 条无效记录")
    else:
        print("  ✅ 没有发现无效记录")
    
    # 3. 检查遗漏的 user_memorials 记录（纪念馆存在但没有关联记录）
    print("\n🔍 检查遗漏的 user_memorials 记录...")
    cursor.execute('''
    SELECT m.id, m.user_id
    FROM memorials m
    LEFT JOIN user_memorials um ON m.id = um.memorial_id
    WHERE um.memorial_id IS NULL
    ''')
    
    missing_records = cursor.fetchall()
    if missing_records:
        print(f"  ⚠️  发现 {len(missing_records)} 条遗漏记录：")
        for memorial_id, user_id in missing_records:
            print(f"    纪念馆 {memorial_id} - 用户 {user_id} (缺少关联记录)")
        
        # 补充遗漏记录
        print("\n🔧 补充遗漏记录...")
        for memorial_id, user_id in missing_records:
            try:
                cursor.execute('''
                INSERT INTO user_memorials (user_id, memorial_id)
                VALUES (?, ?)
                ''', (user_id, memorial_id))
                print(f"  ✅ 已为纪念馆 {memorial_id} 添加关联记录")
            except sqlite3.IntegrityError:
                print(f"  ⚠️  纪念馆 {memorial_id} 的关联记录已存在")
        
        conn.commit()
        print(f"  ✅ 已补充 {len(missing_records)} 条遗漏记录")
    else:
        print("  ✅ 没有发现遗漏记录")
    
    # 4. 重新统计
    print("\n📊 修复后的统计：")
    cursor.execute('''
    SELECT 
        u.id,
        u.email,
        u.nickname,
        COUNT(um.memorial_id) as memorial_count
    FROM users u
    LEFT JOIN user_memorials um ON u.id = um.user_id
    GROUP BY u.id
    ORDER BY memorial_count DESC
    ''')
    
    users = cursor.fetchall()
    for user_id, email, nickname, count in users:
        print(f"  用户 {user_id} ({email or nickname or '未命名'}): {count} 个纪念馆")
    
    conn.close()
    print("\n" + "=" * 50)
    print("✅ 检查完成！")
    print("=" * 50)

if __name__ == "__main__":
    check_and_fix_memorial_count()

