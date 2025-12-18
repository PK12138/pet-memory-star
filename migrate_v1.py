#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V1 数据库迁移脚本（可重复执行）

目标：
- 兼容旧版数据库（字段缺失/表缺失）
- 不依赖服务启动时的“自动迁移”

用法：
  python migrate_v1.py
"""

import os
import sqlite3
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def get_db_path() -> str:
    root = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(root, "app", "pet_memorials.db")


def table_columns(cur: sqlite3.Cursor, table: str) -> set[str]:
    cur.execute(f"PRAGMA table_info({table})")
    return {row[1] for row in cur.fetchall()}


def ensure_column(cur: sqlite3.Cursor, table: str, column_def: str) -> None:
    col_name = column_def.split()[0]
    cols = table_columns(cur, table)
    if col_name in cols:
        print(f"  OK  {table}.{col_name}")
        return
    try:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {column_def}")
        print(f"  ADD {table}.{col_name}")
    except Exception as e:
        print(f"  ERR add {table}.{col_name}: {e}")


def ensure_table(cur: sqlite3.Cursor, create_sql: str, table_name: str) -> None:
    try:
        cur.execute(create_sql)
        print(f"  OK  table {table_name}")
    except Exception as e:
        print(f"  ERR create {table_name}: {e}")


def ensure_index(cur: sqlite3.Cursor, create_sql: str, index_name: str) -> None:
    try:
        cur.execute(create_sql)
        print(f"  OK  index {index_name}")
    except Exception as e:
        print(f"  WARN index {index_name}: {e}")


def migrate() -> int:
    db_path = get_db_path()
    if not os.path.exists(db_path):
        print(f"[ERR] DB file not found: {db_path}")
        return 1

    print(f"[DB] Path: {db_path}")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    try:
        print("\n[1] Ensure users columns")
        # users 表必须先存在
        ensure_table(
            cur,
            """
            CREATE TABLE IF NOT EXISTS users (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              email TEXT UNIQUE,
              password_hash TEXT,
              salt TEXT,
              user_level INTEGER DEFAULT 0,
              is_active BOOLEAN DEFAULT 1,
              email_verified BOOLEAN DEFAULT 0,
              email_verification_token TEXT,
              email_verification_expires TIMESTAMP,
              avatar_url TEXT,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              last_login TIMESTAMP
            )
            """,
            "users",
        )
        ensure_column(cur, "users", "openid TEXT")
        ensure_column(cur, "users", "nickname TEXT")
        ensure_column(cur, "users", "phone TEXT")

        # 尽量补上 openid 唯一性（如果历史数据存在重复，会失败并给出 warning）
        ensure_index(
            cur,
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_openid_unique ON users(openid)",
            "idx_users_openid_unique",
        )

        print("\n[2] Ensure memorials columns")
        # memorials 表必须先存在（旧库可能只有少数字段）
        ensure_table(
            cur,
            """
            CREATE TABLE IF NOT EXISTS memorials (
              id TEXT PRIMARY KEY,
              pet_id TEXT NOT NULL,
              memorial_url TEXT NOT NULL,
              ai_letter TEXT,
              theme_template TEXT DEFAULT 'default',
              is_public BOOLEAN DEFAULT 1,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            "memorials",
        )

        # 纪念馆管理依赖字段（与 migrate_memorial_tables.py 对齐 + V1 补充）
        for col in [
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
            "updated_at TIMESTAMP",
            "ai_letter_unlocked BOOLEAN DEFAULT 0",
        ]:
            ensure_column(cur, "memorials", col)

        print("\n[3] Ensure feedbacks table")
        ensure_table(
            cur,
            """
            CREATE TABLE IF NOT EXISTS feedbacks (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER,
              contact TEXT,
              content TEXT NOT NULL,
              status TEXT DEFAULT 'pending',
              reply TEXT,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            "feedbacks",
        )
        ensure_index(cur, "CREATE INDEX IF NOT EXISTS idx_feedbacks_user ON feedbacks(user_id)", "idx_feedbacks_user")
        ensure_index(cur, "CREATE INDEX IF NOT EXISTS idx_feedbacks_status ON feedbacks(status)", "idx_feedbacks_status")

        print("\n[4] Ensure memorial support tables")
        ensure_table(
            cur,
            """
            CREATE TABLE IF NOT EXISTS user_memorials (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER NOT NULL,
              memorial_id TEXT NOT NULL,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            "user_memorials",
        )
        ensure_index(cur, "CREATE INDEX IF NOT EXISTS idx_user_memorials_user ON user_memorials(user_id)", "idx_user_memorials_user")
        ensure_index(cur, "CREATE INDEX IF NOT EXISTS idx_user_memorials_memorial ON user_memorials(memorial_id)", "idx_user_memorials_memorial")

        ensure_table(
            cur,
            """
            CREATE TABLE IF NOT EXISTS memorial_photos (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              memorial_id TEXT NOT NULL,
              photo_url TEXT NOT NULL,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            "memorial_photos",
        )
        ensure_index(cur, "CREATE INDEX IF NOT EXISTS idx_memorial_photos_memorial ON memorial_photos(memorial_id)", "idx_memorial_photos_memorial")

        ensure_table(
            cur,
            """
            CREATE TABLE IF NOT EXISTS memorial_stats (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              memorial_id TEXT NOT NULL,
              views INTEGER DEFAULT 0,
              likes INTEGER DEFAULT 0,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            "memorial_stats",
        )
        ensure_index(cur, "CREATE INDEX IF NOT EXISTS idx_memorial_stats_memorial ON memorial_stats(memorial_id)", "idx_memorial_stats_memorial")

        conn.commit()
        print("\n[DONE] migrate_v1 finished")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(migrate())


