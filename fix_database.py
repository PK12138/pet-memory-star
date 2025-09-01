#!/usr/bin/env python3
"""
数据库修复脚本 - 更新所有表结构
"""

import sqlite3
import os

def fix_database():
    """修复数据库表结构"""
    print("=== 开始修复数据库表结构 ===")
    
    db_path = "pet_memorials.db"
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("✅ 数据库连接成功")
        
        # 检查当前users表结构
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        print("当前users表结构:")
        for col in columns:
            print(f"  {col[1]} {col[2]} {'UNIQUE' if col[5] else ''}")
        
        # 检查是否需要修复users表
        column_names = [col[1] for col in columns]
        
        if 'username' in column_names or 'phone' in column_names or 'real_name' in column_names:
            print("\n需要修复users表结构...")
            
            # 创建新的users表结构
            cursor.execute("""
                CREATE TABLE users_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    user_level INTEGER DEFAULT 1,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    avatar_url TEXT
                )
            """)
            
            print("✅ 新users表结构创建成功")
            
            # 复制现有数据（如果有的话）
            try:
                cursor.execute("""
                    INSERT INTO users_new (id, email, password_hash, salt, user_level, is_active, created_at, last_login, avatar_url)
                    SELECT id, email, password_hash, salt, user_level, is_active, created_at, last_login, avatar_url
                    FROM users
                """)
                print("✅ users表数据迁移成功")
            except Exception as e:
                print(f"⚠️ users表数据迁移失败（可能是空表）: {e}")
            
            # 删除旧表
            cursor.execute("DROP TABLE users")
            print("✅ 旧users表删除成功")
            
            # 重命名新表
            cursor.execute("ALTER TABLE users_new RENAME TO users")
            print("✅ users表重命名成功")
            
        else:
            print("✅ users表结构已经是最新的，无需修复")
        
        # 检查pets表结构
        cursor.execute("PRAGMA table_info(pets)")
        pet_columns = cursor.fetchall()
        print("\n当前pets表结构:")
        for col in pet_columns:
            print(f"  {col[1]} {col[2]} {'UNIQUE' if col[5] else ''}")
        
        # 检查pets表是否需要修复
        pet_column_names = [col[1] for col in pet_columns]
        
        if 'user_id' not in pet_column_names:
            print("\n需要修复pets表结构...")
            
            # 创建新的pets表结构
            cursor.execute("""
                CREATE TABLE pets_new (
                    id TEXT PRIMARY KEY,
                    user_id INTEGER,
                    name TEXT NOT NULL,
                    species TEXT NOT NULL,
                    breed TEXT,
                    color TEXT,
                    gender TEXT,
                    birth_date TEXT,
                    memorial_date TEXT,
                    weight REAL,
                    personality_type TEXT,
                    status TEXT DEFAULT 'alive',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            print("✅ 新pets表结构创建成功")
            
            # 复制现有数据（如果有的话）
            try:
                cursor.execute("""
                    INSERT INTO pets_new (id, name, species, breed, color, gender, birth_date, memorial_date, weight, personality_type, status, created_at)
                    SELECT id, name, species, breed, color, gender, birth_date, memorial_date, weight, personality_type, status, created_at
                    FROM pets
                """)
                print("✅ pets表数据迁移成功")
            except Exception as e:
                print(f"⚠️ pets表数据迁移失败（可能是空表）: {e}")
            
            # 删除旧表
            cursor.execute("DROP TABLE pets")
            print("✅ 旧pets表删除成功")
            
            # 重命名新表
            cursor.execute("ALTER TABLE pets_new RENAME TO pets")
            print("✅ pets表重命名成功")
            
        else:
            print("✅ pets表结构已经是最新的，无需修复")
        
        # 检查memorials表结构
        cursor.execute("PRAGMA table_info(memorials)")
        memorial_columns = cursor.fetchall()
        print("\n当前memorials表结构:")
        for col in memorial_columns:
            print(f"  {col[1]} {col[2]} {'UNIQUE' if col[5] else ''}")
        
        # 检查memorials表是否需要修复
        memorial_column_names = [col[1] for col in memorial_columns]
        
        if 'theme_template' not in memorial_column_names or 'is_public' not in memorial_column_names:
            print("\n需要修复memorials表结构...")
            
            # 创建新的memorials表结构
            cursor.execute("""
                CREATE TABLE memorials_new (
                    id TEXT PRIMARY KEY,
                    pet_id TEXT NOT NULL,
                    memorial_url TEXT NOT NULL,
                    ai_letter TEXT,
                    theme_template TEXT DEFAULT 'default',
                    is_public BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (pet_id) REFERENCES pets(id)
                )
            """)
            
            print("✅ 新memorials表结构创建成功")
            
            # 复制现有数据（如果有的话）
            try:
                cursor.execute("""
                    INSERT INTO memorials_new (id, pet_id, memorial_url, ai_letter, created_at)
                    SELECT id, pet_id, memorial_url, ai_letter, created_at
                    FROM memorials
                """)
                print("✅ memorials表数据迁移成功")
            except Exception as e:
                print(f"⚠️ memorials表数据迁移失败（可能是空表）: {e}")
            
            # 删除旧表
            cursor.execute("DROP TABLE memorials")
            print("✅ 旧memorials表删除成功")
            
            # 重命名新表
            cursor.execute("ALTER TABLE memorials_new RENAME TO memorials")
            print("✅ memorials表重命名成功")
            
        else:
            print("✅ memorials表结构已经是最新的，无需修复")
        
        # 提交更改
        conn.commit()
        print("\n✅ 数据库修复完成")
        
        # 验证修复结果
        print("\n=== 修复后的表结构 ===")
        
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        print("users表结构:")
        for col in columns:
            print(f"  {col[1]} {col[2]} {'UNIQUE' if col[5] else ''}")
        
        cursor.execute("PRAGMA table_info(pets)")
        pet_columns = cursor.fetchall()
        print("\npets表结构:")
        for col in pet_columns:
            print(f"  {col[1]} {col[2]} {'UNIQUE' if col[5] else ''}")
        
        cursor.execute("PRAGMA table_info(memorials)")
        memorial_columns = cursor.fetchall()
        print("\nmemorials表结构:")
        for col in memorial_columns:
            print(f"  {col[1]} {col[2]} {'UNIQUE' if col[5] else ''}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 数据库修复失败: {e}")
        if 'conn' in locals():
            conn.close()

def test_user_creation():
    """测试用户创建功能"""
    print("\n=== 测试用户创建功能 ===")
    
    try:
        from app.database import Database
        
        db = Database()
        
        # 测试创建用户
        test_email = "test_fix@example.com"
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
    print("开始数据库修复...")
    print("=" * 50)
    
    fix_database()
    test_user_creation()
    
    print("\n" + "=" * 50)
    print("=== 修复完成 ===")

if __name__ == "__main__":
    main()
