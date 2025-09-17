#!/usr/bin/env python3
"""
纪念馆管理功能数据库迁移脚本
添加纪念馆照片表和统计表，更新纪念馆表结构
"""
import sqlite3
import os

def migrate_database():
    """执行数据库迁移"""
    # 数据库路径
    db_path = os.path.join(os.path.dirname(__file__), "app", "pet_memorials.db")
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 开始迁移纪念馆管理功能...")
        
        # 1. 添加纪念馆表新字段
        print("📝 更新纪念馆表结构...")
        new_columns = [
            "user_id INTEGER",
            "pet_name TEXT",
            "species TEXT", 
            "breed TEXT",
            "color TEXT",
            "gender TEXT",
            "birth_date TEXT",
            "memorial_date TEXT",
            "weight REAL",
            "description TEXT",
            "personality TEXT",
            "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        ]
        
        for column in new_columns:
            column_name = column.split()[0]
            try:
                cursor.execute(f"ALTER TABLE memorials ADD COLUMN {column}")
                print(f"  ✅ 添加字段: {column_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"  ⚠️  字段已存在: {column_name}")
                else:
                    print(f"  ❌ 添加字段失败: {column_name} - {e}")
        
        # 2. 创建纪念馆照片表
        print("📷 创建纪念馆照片表...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS memorial_photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memorial_id TEXT NOT NULL,
            photo_url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (memorial_id) REFERENCES memorials (id)
        )
        ''')
        print("  ✅ 纪念馆照片表创建成功")
        
        # 3. 创建纪念馆统计表
        print("📊 创建纪念馆统计表...")
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS memorial_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memorial_id TEXT NOT NULL,
            views INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (memorial_id) REFERENCES memorials (id)
        )
        ''')
        print("  ✅ 纪念馆统计表创建成功")
        
        # 4. 更新现有纪念馆数据
        print("🔄 更新现有纪念馆数据...")
        cursor.execute('''
        UPDATE memorials 
        SET updated_at = CURRENT_TIMESTAMP 
        WHERE updated_at IS NULL
        ''')
        updated_count = cursor.rowcount
        print(f"  ✅ 更新了 {updated_count} 条纪念馆记录")
        
        # 5. 为现有纪念馆创建统计记录
        print("📈 为现有纪念馆创建统计记录...")
        cursor.execute('''
        INSERT INTO memorial_stats (memorial_id, views, likes, created_at)
        SELECT id, 0, 0, CURRENT_TIMESTAMP
        FROM memorials 
        WHERE id NOT IN (SELECT memorial_id FROM memorial_stats)
        ''')
        stats_count = cursor.rowcount
        print(f"  ✅ 创建了 {stats_count} 条统计记录")
        
        conn.commit()
        print("🎉 纪念馆管理功能迁移完成！")
        
        # 显示统计信息
        cursor.execute("SELECT COUNT(*) FROM memorials")
        memorial_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM memorial_photos")
        photo_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM memorial_stats")
        stats_count = cursor.fetchone()[0]
        
        print(f"\n📊 数据库统计:")
        print(f"  - 纪念馆数量: {memorial_count}")
        print(f"  - 照片数量: {photo_count}")
        print(f"  - 统计记录: {stats_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🚀 纪念馆管理功能数据库迁移工具")
    print("=" * 50)
    
    success = migrate_database()
    
    if success:
        print("\n✅ 迁移成功完成！")
        print("现在可以使用纪念馆管理功能了。")
    else:
        print("\n❌ 迁移失败！")
        print("请检查错误信息并重试。")
