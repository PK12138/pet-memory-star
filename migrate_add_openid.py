#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本：为 users 表添加 openid 等字段
用于修复微信登录功能
"""

import sqlite3
import os
import sys

def migrate_database():
    """迁移数据库，添加 openid 字段"""
    # 获取数据库路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, "app", "pet_memorials.db")
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    print(f"📁 数据库路径: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表结构
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 当前 users 表字段: {columns}")
        
        # 添加 openid 字段
        if 'openid' not in columns:
            try:
                cursor.execute('ALTER TABLE users ADD COLUMN openid TEXT UNIQUE')
                print("✅ 已添加 openid 字段")
            except sqlite3.OperationalError as e:
                print(f"⚠️ 添加 openid 字段失败: {e}")
        else:
            print("ℹ️ openid 字段已存在")
        
        # 添加 nickname 字段
        if 'nickname' not in columns:
            try:
                cursor.execute('ALTER TABLE users ADD COLUMN nickname TEXT')
                print("✅ 已添加 nickname 字段")
            except sqlite3.OperationalError as e:
                print(f"⚠️ 添加 nickname 字段失败: {e}")
        else:
            print("ℹ️ nickname 字段已存在")
        
        # 添加 phone 字段
        if 'phone' not in columns:
            try:
                cursor.execute('ALTER TABLE users ADD COLUMN phone TEXT')
                print("✅ 已添加 phone 字段")
            except sqlite3.OperationalError as e:
                print(f"⚠️ 添加 phone 字段失败: {e}")
        else:
            print("ℹ️ phone 字段已存在")
        
        conn.commit()
        
        # 验证迁移结果
        cursor.execute("PRAGMA table_info(users)")
        new_columns = [row[1] for row in cursor.fetchall()]
        print(f"📋 迁移后 users 表字段: {new_columns}")
        
        conn.close()
        
        print("\n✅ 数据库迁移完成！")
        return True
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 开始数据库迁移：添加 openid 字段")
    print("=" * 50)
    print()
    
    success = migrate_database()
    
    if success:
        print("\n" + "=" * 50)
        print("✅ 迁移成功！现在可以测试微信登录了")
        print("=" * 50)
        sys.exit(0)
    else:
        print("\n" + "=" * 50)
        print("❌ 迁移失败，请检查错误信息")
        print("=" * 50)
        sys.exit(1)

