#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def check_database_structure():
    """全面检查数据库结构"""
    print("🔍 全面检查数据库结构...")
    
    db_path = os.path.join(os.path.dirname(__file__), "app", "pet_memorials.db")
    print(f"📁 数据库路径: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. 检查所有表
        print("\n1. 检查所有表:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"   表列表: {[table[0] for table in tables]}")
        
        # 2. 检查users表结构
        print("\n2. 检查users表结构:")
        cursor.execute("PRAGMA table_info(users)")
        users_columns = cursor.fetchall()
        print(f"   users表列: {users_columns}")
        
        # 3. 检查email_codes表结构
        print("\n3. 检查email_codes表结构:")
        cursor.execute("PRAGMA table_info(email_codes)")
        email_codes_columns = cursor.fetchall()
        print(f"   email_codes表列: {email_codes_columns}")
        
        # 4. 检查user_levels表结构
        print("\n4. 检查user_levels表结构:")
        cursor.execute("PRAGMA table_info(user_levels)")
        user_levels_columns = cursor.fetchall()
        print(f"   user_levels表列: {user_levels_columns}")
        
        # 5. 检查用户数据
        print("\n5. 检查用户数据:")
        cursor.execute("SELECT id, email, user_level, is_active, email_verified FROM users")
        users = cursor.fetchall()
        print(f"   用户数据: {users}")
        
        # 6. 检查用户等级数据
        print("\n6. 检查用户等级数据:")
        cursor.execute("SELECT * FROM user_levels")
        levels = cursor.fetchall()
        print(f"   等级数据: {levels}")
        
        # 7. 检查email_codes数据
        print("\n7. 检查email_codes数据:")
        cursor.execute("SELECT email, code, code_type, type, expires_at FROM email_codes LIMIT 5")
        codes = cursor.fetchall()
        print(f"   验证码数据: {codes}")
        
        # 8. 检查外键约束
        print("\n8. 检查外键约束:")
        cursor.execute("PRAGMA foreign_key_list(users)")
        fk_users = cursor.fetchall()
        print(f"   users表外键: {fk_users}")
        
        print("\n✅ 数据库结构检查完成")
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_database_structure()
