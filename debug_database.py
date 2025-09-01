#!/usr/bin/env python3
"""
数据库调试脚本
"""

import sqlite3
import os
from pathlib import Path

def check_database():
    """检查数据库状态"""
    print("=== 数据库调试信息 ===")
    
    # 检查数据库文件
    db_path = "pet_memorials.db"
    print(f"数据库文件路径: {os.path.abspath(db_path)}")
    print(f"数据库文件存在: {os.path.exists(db_path)}")
    
    if os.path.exists(db_path):
        print(f"数据库文件大小: {os.path.getsize(db_path)} 字节")
        print(f"数据库文件权限: {oct(os.stat(db_path).st_mode)[-3:]}")
    
    # 尝试连接数据库
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("✅ 数据库连接成功")
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"数据库中的表: {[table[0] for table in tables]}")
        
        # 检查users表结构
        if 'users' in [table[0] for table in tables]:
            cursor.execute("PRAGMA table_info(users)")
            columns = cursor.fetchall()
            print("users表结构:")
            for col in columns:
                print(f"  {col[1]} {col[2]} {'UNIQUE' if col[5] else ''}")
            
            # 检查现有用户
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"现有用户数量: {user_count}")
            
            if user_count > 0:
                cursor.execute("SELECT id, email, created_at FROM users LIMIT 5")
                users = cursor.fetchall()
                print("前5个用户:")
                for user in users:
                    print(f"  ID: {user[0]}, 邮箱: {user[1]}, 创建时间: {user[2]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")

def test_create_user():
    """测试创建用户功能"""
    print("\n=== 测试创建用户功能 ===")
    
    try:
        from app.database import Database
        
        db = Database()
        
        # 测试创建用户
        test_email = "debug_test@example.com"
        test_password = "123456"
        
        print(f"尝试创建用户: {test_email}")
        user_id = db.create_user(test_email, test_password)
        
        if user_id:
            print(f"✅ 用户创建成功，ID: {user_id}")
            
            # 验证用户是否存在
            cursor = db.conn.cursor()
            cursor.execute("SELECT id, email FROM users WHERE email = ?", (test_email,))
            user = cursor.fetchone()
            if user:
                print(f"✅ 用户验证成功: {user}")
            else:
                print("❌ 用户验证失败")
                
        else:
            print("❌ 用户创建失败")
            
    except Exception as e:
        print(f"❌ 测试创建用户失败: {e}")

def main():
    """主函数"""
    print("开始数据库调试...")
    print("=" * 50)
    
    check_database()
    test_create_user()
    
    print("\n" + "=" * 50)
    print("=== 调试完成 ===")

if __name__ == "__main__":
    main()
