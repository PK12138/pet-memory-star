#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库完整性检查脚本
检查所有表结构、索引、数据完整性
"""

import sqlite3
import os
from datetime import datetime

def check_database():
    """检查数据库完整性"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, "app", "pet_memorials.db")
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    print(f"📁 数据库路径: {db_path}\n")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    print("="*60)
    print("📊 数据库完整性检查")
    print("="*60 + "\n")
    
    # 必需的表
    required_tables = [
        'users', 'user_sessions', 'memorials', 'pets', 
        'photos', 'messages', 'feedbacks', 'user_coins',
        'coin_transactions', 'payment_orders'
    ]
    
    print("✅ 表结构检查:")
    for table in required_tables:
        if table in tables:
            # 检查表记录数
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  ✅ {table}: {count} 条记录")
        else:
            print(f"  ❌ {table}: 表不存在")
    
    print("\n" + "="*60)
    print("🔍 关键字段检查:")
    print("="*60 + "\n")
    
    # 检查users表关键字段
    cursor.execute("PRAGMA table_info(users)")
    user_columns = [row[1] for row in cursor.fetchall()]
    required_user_columns = ['id', 'email', 'openid', 'nickname', 'user_level']
    for col in required_user_columns:
        if col in user_columns:
            print(f"  ✅ users.{col}: 存在")
        else:
            print(f"  ❌ users.{col}: 不存在")
    
    # 检查feedbacks表
    if 'feedbacks' in tables:
        cursor.execute("PRAGMA table_info(feedbacks)")
        feedback_columns = [row[1] for row in cursor.fetchall()]
        required_feedback_columns = ['id', 'user_id', 'contact', 'content', 'status']
        for col in required_feedback_columns:
            if col in feedback_columns:
                print(f"  ✅ feedbacks.{col}: 存在")
            else:
                print(f"  ❌ feedbacks.{col}: 不存在")
    
    print("\n" + "="*60)
    print("📈 数据统计:")
    print("="*60 + "\n")
    
    # 统计各表数据
    stats = {}
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            stats[table] = count
        except:
            stats[table] = "错误"
    
    for table, count in sorted(stats.items()):
        print(f"  {table}: {count}")
    
    print("\n" + "="*60)
    print("🔗 外键完整性检查:")
    print("="*60 + "\n")
    
    # 检查memorials和users的关联
    cursor.execute("""
        SELECT COUNT(*) FROM memorials m 
        LEFT JOIN users u ON m.user_id = u.id 
        WHERE m.user_id IS NOT NULL AND u.id IS NULL
    """)
    orphan_memorials = cursor.fetchone()[0]
    if orphan_memorials == 0:
        print("  ✅ memorials 外键完整性: 正常")
    else:
        print(f"  ⚠️  memorials 外键完整性: 发现 {orphan_memorials} 条孤立记录")
    
    # 检查feedbacks和users的关联
    if 'feedbacks' in tables:
        cursor.execute("""
            SELECT COUNT(*) FROM feedbacks f 
            LEFT JOIN users u ON f.user_id = u.id 
            WHERE f.user_id IS NOT NULL AND u.id IS NULL
        """)
        orphan_feedbacks = cursor.fetchone()[0]
        if orphan_feedbacks == 0:
            print("  ✅ feedbacks 外键完整性: 正常")
        else:
            print(f"  ⚠️  feedbacks 外键完整性: 发现 {orphan_feedbacks} 条孤立记录")
    
    print("\n" + "="*60)
    print("✅ 检查完成")
    print("="*60 + "\n")
    
    conn.close()
    return True

if __name__ == "__main__":
    check_database()

