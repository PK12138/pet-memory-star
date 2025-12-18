#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库完整性检查脚本
检查所有表结构、索引、数据完整性
"""

import os
import sqlite3
import sys
from datetime import datetime

# Windows PowerShell 默认控制台编码可能为 GBK，直接打印 emoji 会触发 UnicodeEncodeError。
# 这里尽量将 stdout 切到 UTF-8，并避免输出 emoji，保证脚本在 Windows/Linux 都可运行。
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

def check_database():
    """检查数据库完整性"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, "app", "pet_memorials.db")
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    print(f"[DB] Path: {db_path}\n")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    print("=" * 60)
    print("[DB] Integrity Check")
    print("=" * 60 + "\n")
    
    # V1 必需的表（缺失则提示，但不直接崩溃）
    required_tables = [
        'users', 'user_sessions', 'memorials', 'pets', 
        'photos', 'messages', 'feedbacks', 'user_coins',
        'coin_transactions', 'payment_orders'
    ]
    
    print("[1] Table check:")
    for table in required_tables:
        if table in tables:
            # 检查表记录数
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  OK  {table}: {count} rows")
        else:
            print(f"  ERR {table}: missing")
    
    print("\n" + "=" * 60)
    print("[2] Key columns check:")
    print("=" * 60 + "\n")
    
    # 检查 users 表关键字段
    cursor.execute("PRAGMA table_info(users)")
    user_columns = [row[1] for row in cursor.fetchall()]
    required_user_columns = ['id', 'email', 'openid', 'nickname', 'user_level']
    for col in required_user_columns:
        if col in user_columns:
            print(f"  OK  users.{col}: present")
        else:
            print(f"  WARN users.{col}: missing (need migration)")
    
    # 检查 feedbacks 表
    if 'feedbacks' in tables:
        cursor.execute("PRAGMA table_info(feedbacks)")
        feedback_columns = [row[1] for row in cursor.fetchall()]
        required_feedback_columns = ['id', 'user_id', 'contact', 'content', 'status']
        for col in required_feedback_columns:
            if col in feedback_columns:
                print(f"  OK  feedbacks.{col}: present")
            else:
                print(f"  WARN feedbacks.{col}: missing (need migration)")
    else:
        print("  WARN feedbacks: table missing (need migration)")
    
    print("\n" + "=" * 60)
    print("[3] Table stats:")
    print("=" * 60 + "\n")
    
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
    
    print("\n" + "=" * 60)
    print("[4] Foreign-key sanity check:")
    print("=" * 60 + "\n")
    
    # 检查 user_memorials 关联（比 memorials.user_id 更稳定；旧库可能没有 user_id 列）
    if 'user_memorials' in tables:
        cursor.execute("""
            SELECT COUNT(*) FROM user_memorials um
            LEFT JOIN users u ON um.user_id = u.id
            WHERE u.id IS NULL
        """)
        orphan_um_users = cursor.fetchone()[0]
        if orphan_um_users == 0:
            print("  OK  user_memorials -> users: OK")
        else:
            print(f"  WARN user_memorials -> users: {orphan_um_users} orphan rows")

        cursor.execute("""
            SELECT COUNT(*) FROM user_memorials um
            LEFT JOIN memorials m ON um.memorial_id = m.id
            WHERE m.id IS NULL
        """)
        orphan_um_memorials = cursor.fetchone()[0]
        if orphan_um_memorials == 0:
            print("  OK  user_memorials -> memorials: OK")
        else:
            print(f"  WARN user_memorials -> memorials: {orphan_um_memorials} orphan rows")
    else:
        print("  WARN user_memorials: table missing (need migration)")
    
    # 检查feedbacks和users的关联
    if 'feedbacks' in tables:
        cursor.execute("""
            SELECT COUNT(*) FROM feedbacks f 
            LEFT JOIN users u ON f.user_id = u.id 
            WHERE f.user_id IS NOT NULL AND u.id IS NULL
        """)
        orphan_feedbacks = cursor.fetchone()[0]
        if orphan_feedbacks == 0:
            print("  OK  feedbacks -> users: OK")
        else:
            print(f"  WARN feedbacks -> users: {orphan_feedbacks} orphan rows")
    
    print("\n" + "=" * 60)
    print("[DONE] Check finished")
    print("=" * 60 + "\n")
    
    conn.close()
    return True

if __name__ == "__main__":
    check_database()

