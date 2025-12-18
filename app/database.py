import sqlite3
import os
import hashlib
import secrets
from datetime import datetime, timedelta
import json

class Database:
    def __init__(self, db_path=None):
        if db_path is None:
            # 获取当前文件所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(current_dir, "pet_memorials.db")
        self.conn = sqlite3.connect(db_path)
        self._create_tables()
    
    def _create_tables(self):
        cursor = self.conn.cursor()
        
        # ============ 星币系统相关表 ============
        
        # 用户星币表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_coins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            balance INTEGER DEFAULT 0,
            total_earned INTEGER DEFAULT 0,
            total_spent INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # 星币交易记录表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS coin_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            type TEXT NOT NULL,
            description TEXT,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_coin_transactions_user ON coin_transactions(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_coin_transactions_type ON coin_transactions(type)')
        
        # 每日签到记录表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_sign_in (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            sign_date DATE NOT NULL,
            continuous_days INTEGER DEFAULT 1,
            reward_coins INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, sign_date),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_daily_sign_in_user ON daily_sign_in(user_id)')
        
        # 任务完成记录表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            task_type TEXT NOT NULL,
            completion_date DATE NOT NULL,
            completion_count INTEGER DEFAULT 1,
            reward_coins INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_completions_user ON task_completions(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_completions_date ON task_completions(completion_date)')
        
        # 激励广告观看记录表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ad_views (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            ad_unit_id TEXT NOT NULL,
            view_date DATE NOT NULL,
            view_count INTEGER DEFAULT 1,
            reward_coins INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ad_views_user ON ad_views(user_id)')
        
        # ============ 原有系统表 ============
        
        # 用户表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password_hash TEXT,
            salt TEXT,
            openid TEXT UNIQUE,
            nickname TEXT,
            phone TEXT,
            user_level INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            email_verified BOOLEAN DEFAULT 0,
            email_verification_token TEXT,
            email_verification_expires TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            avatar_url TEXT
        )
        ''')
        
        # 用户会话表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            user_agent TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # 密码重置表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_resets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            reset_token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            used BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # 用户等级表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_levels (
            level INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            max_memorials INTEGER DEFAULT 1,
            max_photos INTEGER DEFAULT 10,
            can_use_ai BOOLEAN DEFAULT 0,
            can_export BOOLEAN DEFAULT 0,
            can_custom_domain BOOLEAN DEFAULT 0,
            price_monthly REAL DEFAULT 0.0,
            price_yearly REAL DEFAULT 0.0,
            description TEXT
        )
        ''')
        
        # 充值订单表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS payment_orders (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            order_type TEXT NOT NULL,  -- 'upgrade_monthly', 'upgrade_yearly', 'custom'
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'CNY',
            payment_method TEXT,  -- 'wechat', 'alipay', 'bank'
            payment_status TEXT DEFAULT 'pending',  -- 'pending', 'paid', 'failed', 'cancelled', 'refunded'
            payment_platform TEXT,  -- 支付平台返回的交易号
            payment_time TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            description TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # 用户余额表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_balance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            balance REAL DEFAULT 0.0,
            frozen_balance REAL DEFAULT 0.0,
            total_recharged REAL DEFAULT 0.0,
            total_consumed REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # 充值记录表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS recharge_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            order_id TEXT NOT NULL,
            amount REAL NOT NULL,
            balance_before REAL NOT NULL,
            balance_after REAL NOT NULL,
            recharge_type TEXT NOT NULL,  -- 'upgrade', 'balance', 'gift'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (order_id) REFERENCES payment_orders(id)
        )
        ''')
        
        # 纪念馆照片表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS memorial_photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memorial_id TEXT NOT NULL,
            photo_url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (memorial_id) REFERENCES memorials (id)
        )
        ''')
        
        # 纪念馆统计表
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
        
        # 用户权限表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            permission_name TEXT NOT NULL,
            granted BOOLEAN DEFAULT 1,
            granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            granted_by INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (granted_by) REFERENCES users(id)
        )
        ''')
        
        # 用户纪念馆关联表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_memorials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            memorial_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (memorial_id) REFERENCES memorials(id)
        )
        ''')
        
        # 宠物基本信息表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS pets (
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
            status TEXT DEFAULT 'alive',  -- 'alive' 或 'passed'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # 纪念馆表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS memorials (
            id TEXT PRIMARY KEY,
            pet_id TEXT NOT NULL,
            memorial_url TEXT NOT NULL,
            ai_letter TEXT,
            ai_letter_unlocked BOOLEAN DEFAULT 0,
            theme_template TEXT DEFAULT 'default',
            is_public BOOLEAN DEFAULT 1,
            user_id INTEGER,
            pet_name TEXT,
            species TEXT,
            breed TEXT,
            color TEXT,
            gender TEXT,
            birth_date TEXT,
            memorial_date TEXT,
            weight REAL,
            description TEXT,
            personality TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pet_id) REFERENCES pets(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # 检查并添加 ai_letter_unlocked 字段（兼容旧数据库）
        try:
            cursor.execute('ALTER TABLE memorials ADD COLUMN ai_letter_unlocked BOOLEAN DEFAULT 0')
            print("✅ 已添加 ai_letter_unlocked 字段到 memorials 表")
        except sqlite3.OperationalError:
            pass
        
        # AI对话每日计数表（用于免费次数统计）
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_chat_daily_counts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            memorial_id TEXT NOT NULL,
            chat_date DATE NOT NULL,
            free_count INTEGER DEFAULT 0,
            paid_count INTEGER DEFAULT 0,
            last_chat_time TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, memorial_id, chat_date),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (memorial_id) REFERENCES memorials(id)
        )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ai_chat_daily_user ON ai_chat_daily_counts(user_id, memorial_id, chat_date)')
        
        # 性格测试答案表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS personality_tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id TEXT NOT NULL,
            question_id INTEGER NOT NULL,
            answer TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pet_id) REFERENCES pets(id)
        )
        ''')
        
        # 照片表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id TEXT NOT NULL,
            photo_url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pet_id) REFERENCES pets(id)
        )
        ''')
        
        # 留言表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id TEXT NOT NULL,
            visitor_name TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pet_id) REFERENCES pets(id)
        )
        ''')
        
        # 纪念日提醒表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id TEXT NOT NULL,
            reminder_type TEXT NOT NULL,
            reminder_date TEXT NOT NULL,
            custom_name TEXT,
            custom_description TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pet_id) REFERENCES pets(id)
        )
        ''')
        
        # 心情日记表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS mood_diaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id TEXT NOT NULL,
            mood_type TEXT NOT NULL,
            mood_score INTEGER NOT NULL,
            diary_content TEXT,
            weather TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pet_id) REFERENCES pets(id)
        )
        ''')
        
        # 梦境日记表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS dream_diaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memorial_id TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            dream_date DATE NOT NULL,
            dream_time TEXT,
            dream_content TEXT NOT NULL,
            emotion_type TEXT,
            mood_score INTEGER,
            tags TEXT,
            ai_analysis TEXT,
            is_private BOOLEAN DEFAULT 0,
            is_favorite BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (memorial_id) REFERENCES memorials(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # 访问统计表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS visit_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memorial_id TEXT NOT NULL,
            visitor_ip TEXT,
            visit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_agent TEXT,
            FOREIGN KEY (memorial_id) REFERENCES memorials(id)
        )
        ''')
        
        # AI对话消息表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memorial_id TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,  -- 'user' 或 'assistant'
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (memorial_id) REFERENCES memorials(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # 情绪记录表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS emotion_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memorial_id TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            emotion TEXT NOT NULL,  -- happy/sad/anxious/calm/angry/lonely/nostalgic
            intensity REAL DEFAULT 0.5,
            keywords TEXT,  -- JSON格式
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (memorial_id) REFERENCES memorials(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # 问候消息表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS greeting_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memorial_id TEXT NOT NULL,
            greeting_type TEXT NOT NULL,  -- morning/evening/special_day/random
            content TEXT NOT NULL,
            is_read BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (memorial_id) REFERENCES memorials(id)
        )
        ''')
        
        # 宠物状态表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS pet_states (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memorial_id TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            mood INTEGER DEFAULT 50,  -- 0-100
            energy INTEGER DEFAULT 50,  -- 0-100
            intimacy INTEGER DEFAULT 0,  -- 0-100
            last_interaction TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (memorial_id) REFERENCES memorials(id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(memorial_id, user_id)
        )
        ''')
        
        # 互动记录表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS interaction_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memorial_id TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            interaction_type TEXT NOT NULL,  -- feed/play/walk/pet
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (memorial_id) REFERENCES memorials(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # 邮箱验证码表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            code TEXT NOT NULL,
            type TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 密码重置令牌表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            token TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            used BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 用户反馈表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedbacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            contact TEXT,
            content TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            reply TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedbacks_user ON feedbacks(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedbacks_status ON feedbacks(status)')
        
        # 初始化用户等级数据
        self._init_user_levels()
        
        self.conn.commit()
    
    def _init_user_levels(self):
        """初始化用户等级数据"""
        cursor = self.conn.cursor()
        
        # 检查是否已存在等级数据
        cursor.execute("SELECT COUNT(*) FROM user_levels")
        if cursor.fetchone()[0] == 0:
            # 首次初始化：直接插入最新配置
            levels = [
                (0, "免费用户", 3, 6, 0, 0, 0, 0.0, 0.0, "基础功能，最多 3 个纪念馆，6 张照片"),
                (1, "高级用户", -1, -1, 1, 1, 0, 29.9, 299.0, "无限纪念馆，无限照片，AI 功能，数据导出")
            ]

            cursor.executemany(
                '''
                INSERT INTO user_levels (
                    level, name, max_memorials, max_photos,
                    can_use_ai, can_export, can_custom_domain,
                    price_monthly, price_yearly, description
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                levels
            )
            self.conn.commit()
        else:
            # 已有数据时，确保免费用户的上限至少为 3
            cursor.execute(
                "UPDATE user_levels SET max_memorials = 3, description = ? WHERE level = 0 AND max_memorials < 3",
                ("基础功能，最多 3 个纪念馆，6 张照片",)
            )
            self.conn.commit()

    # 用户相关方法
    def create_user(self, email, password):
        """创建新用户（邮箱注册）"""
        cursor = self.conn.cursor()
        
        # 先检查邮箱是否已存在
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            return None  # 邮箱已存在
        
        # 生成盐值和密码哈希
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        
        # 生成邮箱验证令牌
        verification_token = secrets.token_urlsafe(32)
        verification_expires = datetime.now() + timedelta(hours=24)
        
        try:
            cursor.execute('''
            INSERT INTO users (email, password_hash, salt, email_verification_token, email_verification_expires, user_level)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (email, password_hash, salt, verification_token, verification_expires, 0))
            
            user_id = cursor.lastrowid
            self.conn.commit()
            return {"user_id": user_id, "verification_token": verification_token}
        except Exception as e:
            print(f"创建用户失败: {e}")
            return None
    
    def create_user_by_openid(self, openid, nickname=None, avatar_url=None):
        """通过 openid 创建新用户（微信登录）"""
        cursor = self.conn.cursor()
        
        # 先检查 openid 是否已存在
        cursor.execute('SELECT id FROM users WHERE openid = ?', (openid,))
        if cursor.fetchone():
            return None  # openid 已存在
        
        try:
            # 生成一个临时邮箱（格式：wx_{openid}@wechat.temp）
            temp_email = f"wx_{openid[:8]}@wechat.temp"
            
            # 创建用户（不需要密码）
            cursor.execute('''
            INSERT INTO users (openid, email, nickname, avatar_url, user_level, is_active, email_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (openid, temp_email, nickname or '微信用户', avatar_url, 0, 1, 0))
            
            user_id = cursor.lastrowid
            self.conn.commit()
            
            # 返回用户信息
            return {
                'id': user_id,
                'openid': openid,
                'email': temp_email,
                'nickname': nickname or '微信用户',
                'avatar_url': avatar_url or '',
                'user_level': 0,
                'is_active': 1,
                'email_verified': 0
            }
        except Exception as e:
            print(f"通过 openid 创建用户失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def verify_user(self, email, password):
        """验证用户登录"""
        cursor = self.conn.cursor()
        
        # 只支持邮箱登录
        cursor.execute('''
        SELECT id, email, password_hash, salt, user_level, is_active
        FROM users 
        WHERE email = ? AND is_active = 1
        ''', (email,))
        
        user = cursor.fetchone()
        if not user:
            return None
        
        user_id, email, stored_hash, salt, user_level, is_active = user
        
        # 验证密码
        input_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        if input_hash == stored_hash:
            # 更新最后登录时间
            cursor.execute('''
            UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
            ''', (user_id,))
            self.conn.commit()
            
            return {
                'id': user_id,
                'email': email,
                'user_level': user_level,
                'is_active': is_active
            }
        
        return None
    
    def verify_email(self, verification_token):
        """验证邮箱"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
        SELECT id, email FROM users 
        WHERE email_verification_token = ? 
        AND email_verification_expires > CURRENT_TIMESTAMP
        AND email_verified = 0
        ''', (verification_token,))
        
        user = cursor.fetchone()
        if not user:
            return None
        
        try:
            cursor.execute('''
            UPDATE users 
            SET email_verified = 1, 
                email_verification_token = NULL, 
                email_verification_expires = NULL
            WHERE id = ?
            ''', (user[0],))
            
            self.conn.commit()
            return {"user_id": user[0], "email": user[1]}
        except Exception as e:
            print(f"邮箱验证失败: {e}")
            return None
    
    def resend_verification_email(self, email):
        """重新发送验证邮件"""
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT id, email_verified FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        if not user:
            return None
        
        if user[1]:  # 如果已经验证过
            return None
        
        # 生成新的验证令牌
        verification_token = secrets.token_urlsafe(32)
        verification_expires = datetime.now() + timedelta(hours=24)
        
        try:
            cursor.execute('''
            UPDATE users 
            SET email_verification_token = ?, 
                email_verification_expires = ?
            WHERE id = ?
            ''', (verification_token, verification_expires, user[0]))
            
            self.conn.commit()
            return verification_token
        except Exception as e:
            print(f"重新生成验证令牌失败: {e}")
            return None
    
    def create_password_reset_token(self, email):
        """创建密码重置令牌"""
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT id FROM users WHERE email = ? AND email_verified = 1', (email,))
        user = cursor.fetchone()
        if not user:
            return None
        
        # 生成重置令牌
        reset_token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=1)
        
        try:
            cursor.execute('''
            INSERT INTO password_resets (user_id, reset_token, expires_at)
            VALUES (?, ?, ?)
            ''', (user[0], reset_token, expires_at))
            
            self.conn.commit()
            return reset_token
        except Exception as e:
            print(f"创建密码重置令牌失败: {e}")
            return None
    
    def verify_password_reset_token(self, reset_token):
        """验证密码重置令牌"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
        SELECT user_id FROM password_resets 
        WHERE reset_token = ? 
        AND expires_at > CURRENT_TIMESTAMP 
        AND used = 0
        ''', (reset_token,))
        
        result = cursor.fetchone()
        return result[0] if result else None
    
    def reset_password(self, reset_token, new_password):
        """重置密码"""
        cursor = self.conn.cursor()
        
        user_id = self.verify_password_reset_token(reset_token)
        if not user_id:
            return False
        
        # 生成新的盐值和密码哈希
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((new_password + salt).encode()).hexdigest()
        
        try:
            # 更新密码
            cursor.execute('''
            UPDATE users 
            SET password_hash = ?, salt = ?
            WHERE id = ?
            ''', (password_hash, salt, user_id))
            
            # 标记重置令牌为已使用
            cursor.execute('''
            UPDATE password_resets 
            SET used = 1
            WHERE reset_token = ?
            ''', (reset_token,))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"重置密码失败: {e}")
            return False
    
    def create_session(self, user_id, ip_address=None, user_agent=None):
        """创建用户会话"""
        cursor = self.conn.cursor()
        
        # 生成会话令牌
        session_token = secrets.token_urlsafe(32)
        # 使用 datetime.utcnow() 确保与 SQLite 的 CURRENT_TIMESTAMP 一致
        expires_at = datetime.utcnow() + timedelta(days=30)  # 30天有效期
        
        print(f"🔑 创建会话: user_id={user_id}, token={session_token[:20]}..., expires_at={expires_at}")
        
        cursor.execute('''
        INSERT INTO user_sessions (user_id, session_token, expires_at, ip_address, user_agent)
        VALUES (?, ?, ?, ?, ?)
        ''', (user_id, session_token, expires_at, ip_address, user_agent))
        
        self.conn.commit()
        return session_token
    
    def get_user_by_session(self, session_token):
        """通过会话令牌获取用户信息"""
        cursor = self.conn.cursor()
        
        print(f"🔍 查询会话: {session_token[:20] if session_token else 'None'}...")
        
        # 先检查会话是否存在
        cursor.execute('''
        SELECT s.user_id, s.expires_at, datetime('now') as current_time
        FROM user_sessions s
        WHERE s.session_token = ?
        ''', (session_token,))
        
        session_info = cursor.fetchone()
        if session_info:
            print(f"🔍 会话信息: user_id={session_info[0]}, expires_at={session_info[1]}, current_time={session_info[2]}")
        else:
            print(f"❌ 会话不存在")
            return None
        
        # 查询用户信息（包含过期检查）
        cursor.execute('''
        SELECT u.id, u.email, u.user_level, u.is_active, u.email_verified
        FROM users u
        JOIN user_sessions s ON u.id = s.user_id
        WHERE s.session_token = ? AND s.expires_at > datetime('now')
        ''', (session_token,))
        
        user = cursor.fetchone()
        print(f"🔍 数据库查询结果: {user}")
        
        if user:
            return {
                'id': user[0],
                'email': user[1],
                'user_level': user[2],
                'is_active': user[3],
                'email_verified': user[4]
            }
        return None
    
    def get_user_by_id(self, user_id):
        """通过用户ID获取用户信息"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
        SELECT id, email, user_level, is_active, email_verified
        FROM users 
        WHERE id = ? AND is_active = 1
        ''', (user_id,))
        
        user = cursor.fetchone()
        if user:
            return {
                'id': user[0],
                'email': user[1],
                'user_level': user[2],
                'is_active': user[3],
                'email_verified': user[4]
            }
        return None
    
    def delete_session(self, session_token):
        """删除会话"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM user_sessions WHERE session_token = ?', (session_token,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def get_user_level_info(self, level):
        """获取用户等级信息"""
        cursor = self.conn.cursor()
        
        print(f"🔍 查询用户等级信息: {level} (类型: {type(level)})")
        
        # 确保level是整数
        try:
            level = int(level)
        except (ValueError, TypeError):
            print(f"⚠️ 用户等级类型错误: {level}, 使用默认等级0")
            level = 0
        
        cursor.execute('''
        SELECT level, name, max_memorials, max_photos, can_use_ai, can_export, can_custom_domain, price_monthly, price_yearly, description
        FROM user_levels WHERE level = ?
        ''', (level,))
        
        result = cursor.fetchone()
        print(f"🔍 等级查询结果: {result}")
        return result
    
    def get_all_user_levels(self):
        """获取所有用户等级信息"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT level, name, max_memorials, max_photos, can_use_ai, can_export, can_custom_domain, price_monthly, price_yearly, description
        FROM user_levels ORDER BY level
        ''')
        levels = cursor.fetchall()
        
        result = []
        for level in levels:
            result.append({
                "level": level[0],
                "name": level[1],
                "max_memorials": level[2],
                "max_photos": level[3],
                "can_use_ai": level[4],
                "can_export": level[5],
                "can_custom_domain": level[6],
                "price_monthly": level[7],
                "price_yearly": level[8],
                "description": level[9]
            })
        
        return result
    
    def get_user_memorials(self, user_id):
        """获取用户的所有纪念馆"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT m.id, m.memorial_url, p.name, p.species, m.created_at
        FROM memorials m
        JOIN pets p ON m.pet_id = p.id
        JOIN user_memorials um ON m.id = um.memorial_id
        WHERE um.user_id = ?
        ORDER BY m.created_at DESC
        ''', (user_id,))
        
        results = cursor.fetchall()
        memorials = []
        for row in results:
            memorials.append({
                'id': row[0],
                'memorial_url': row[1],
                'name': row[2],
                'species': row[3],
                'created_at': row[4]
            })
        return memorials
    
    def link_memorial_to_user(self, user_id, memorial_id):
        """将纪念馆关联到用户"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO user_memorials (user_id, memorial_id)
            VALUES (?, ?)
            ''', (user_id, memorial_id))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_user_memorial_count(self, user_id):
        """获取用户的纪念馆数量"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT COUNT(*) FROM user_memorials WHERE user_id = ?
        ''', (user_id,))
        return cursor.fetchone()[0]
    
    def get_memorial_photo_count(self, memorial_id):
        """获取纪念馆的照片数量"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT COUNT(*) FROM memorial_photos WHERE memorial_id = ?
        ''', (memorial_id,))
        return cursor.fetchone()[0]
    
    def update_user_level(self, user_id, new_level):
        """更新用户等级"""
        cursor = self.conn.cursor()
        cursor.execute('''
        UPDATE users SET user_level = ? WHERE id = ?
        ''', (new_level, user_id))
        self.conn.commit()
        return cursor.rowcount > 0

    # 原有的方法保持不变
    def create_pet_record(self, pet_id, name, species, breed, color, gender, birth_date, memorial_date, weight, user_id=None, status='alive'):
        """创建宠物记录"""
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO pets (id, user_id, name, species, breed, color, gender, birth_date, memorial_date, weight, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (pet_id, user_id, name, species, breed, color, gender, birth_date, memorial_date, weight, status))
        self.conn.commit()
    
    def get_pet_by_id(self, pet_id):
        """根据ID获取宠物信息"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT id, user_id, name, species, breed, color, gender, birth_date, memorial_date, weight, status, personality_type
        FROM pets
        WHERE id = ?
        ''', (pet_id,))
        
        result = cursor.fetchone()
        if result:
            return {
                'id': result[0],
                'user_id': result[1],
                'name': result[2],
                'species': result[3],
                'breed': result[4],
                'color': result[5],
                'gender': result[6],
                'birth_date': result[7],
                'memorial_date': result[8],
                'weight': result[9],
                'status': result[10],
                'personality_type': result[11] if len(result) > 11 else ''
            }
        return None
    
    def create_memorial_record(self, memorial_id, pet_id, memorial_url, ai_letter="", user_id=None, description="", personality=""):
        """创建纪念馆记录"""
        cursor = self.conn.cursor()
        
        # 获取宠物信息以填充冗余字段
        pet_info = self.get_pet_by_id(pet_id)
        
        cursor.execute('''
        INSERT INTO memorials (id, pet_id, memorial_url, ai_letter, user_id, 
                               pet_name, species, breed, color, gender, 
                               birth_date, memorial_date, weight, description, personality)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            memorial_id, 
            pet_id, 
            memorial_url, 
            ai_letter,
            user_id,
            pet_info.get('name', '') if pet_info else '',
            pet_info.get('species', '') if pet_info else '',
            pet_info.get('breed', '') if pet_info else '',
            pet_info.get('color', '') if pet_info else '',
            pet_info.get('gender', '') if pet_info else '',
            pet_info.get('birth_date', '') if pet_info else '',
            pet_info.get('memorial_date', '') if pet_info else '',
            pet_info.get('weight', 0.0) if pet_info else 0.0,
            description,
            personality
        ))
        self.conn.commit()
    
    def save_personality_test(self, pet_id, question_id, answer):
        """保存性格测试答案"""
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO personality_tests (pet_id, question_id, answer)
        VALUES (?, ?, ?)
        ''', (pet_id, question_id, answer))
        self.conn.commit()
    
    def get_personality_test_answers(self, pet_id):
        """获取宠物的性格测试答案"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT question_id, answer FROM personality_tests 
        WHERE pet_id = ? ORDER BY question_id
        ''', (pet_id,))
        return dict(cursor.fetchall())
    
    def update_pet_personality(self, pet_id, personality_type):
        """更新宠物的性格类型"""
        cursor = self.conn.cursor()
        cursor.execute('''
        UPDATE pets SET personality_type = ? WHERE id = ?
        ''', (personality_type, pet_id))
        self.conn.commit()
    
    def update_memorial_ai_letter(self, memorial_id, ai_letter):
        """更新纪念馆的AI信件"""
        cursor = self.conn.cursor()
        cursor.execute('''
        UPDATE memorials SET ai_letter = ? WHERE id = ?
        ''', (ai_letter, memorial_id))
        self.conn.commit()
    
    def unlock_ai_letter(self, memorial_id):
        """解锁AI信件"""
        cursor = self.conn.cursor()
        cursor.execute('''
        UPDATE memorials SET ai_letter_unlocked = 1 WHERE id = ?
        ''', (memorial_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def get_ai_chat_daily_count(self, user_id, memorial_id, chat_date=None):
        """获取AI对话每日计数"""
        if chat_date is None:
            from datetime import date
            chat_date = date.today().isoformat()
        
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT free_count, paid_count FROM ai_chat_daily_counts
        WHERE user_id = ? AND memorial_id = ? AND chat_date = ?
        ''', (user_id, memorial_id, chat_date))
        
        result = cursor.fetchone()
        if result:
            return {
                'free_count': result[0],
                'paid_count': result[1]
            }
        return {'free_count': 0, 'paid_count': 0}
    
    def increment_ai_chat_count(self, user_id, memorial_id, is_free=True, chat_date=None):
        """增加AI对话计数"""
        if chat_date is None:
            from datetime import date, datetime
            chat_date = date.today().isoformat()
        
        cursor = self.conn.cursor()
        
        # 检查是否存在记录
        cursor.execute('''
        SELECT id FROM ai_chat_daily_counts
        WHERE user_id = ? AND memorial_id = ? AND chat_date = ?
        ''', (user_id, memorial_id, chat_date))
        
        exists = cursor.fetchone()
        
        if exists:
            # 更新计数
            if is_free:
                cursor.execute('''
                UPDATE ai_chat_daily_counts 
                SET free_count = free_count + 1, last_chat_time = CURRENT_TIMESTAMP
                WHERE user_id = ? AND memorial_id = ? AND chat_date = ?
                ''', (user_id, memorial_id, chat_date))
            else:
                cursor.execute('''
                UPDATE ai_chat_daily_counts 
                SET paid_count = paid_count + 1, last_chat_time = CURRENT_TIMESTAMP
                WHERE user_id = ? AND memorial_id = ? AND chat_date = ?
                ''', (user_id, memorial_id, chat_date))
        else:
            # 创建新记录
            if is_free:
                cursor.execute('''
                INSERT INTO ai_chat_daily_counts (user_id, memorial_id, chat_date, free_count, paid_count, last_chat_time)
                VALUES (?, ?, ?, 1, 0, CURRENT_TIMESTAMP)
                ''', (user_id, memorial_id, chat_date))
            else:
                cursor.execute('''
                INSERT INTO ai_chat_daily_counts (user_id, memorial_id, chat_date, free_count, paid_count, last_chat_time)
                VALUES (?, ?, ?, 0, 1, CURRENT_TIMESTAMP)
                ''', (user_id, memorial_id, chat_date))
        
        self.conn.commit()
        
        # 返回更新后的计数
        return self.get_ai_chat_daily_count(user_id, memorial_id, chat_date)
    
    def update_memorial_url(self, memorial_id, memorial_url):
        """更新纪念馆的URL"""
        cursor = self.conn.cursor()
        cursor.execute('''
        UPDATE memorials SET memorial_url = ? WHERE id = ?
        ''', (memorial_url, memorial_id))
        self.conn.commit()
    
    def save_photo(self, pet_id, photo_url):
        """保存照片记录"""
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO photos (pet_id, photo_url)
        VALUES (?, ?)
        ''', (pet_id, photo_url))
        self.conn.commit()
    
    def save_message(self, pet_id, visitor_name, message):
        """保存访客留言"""
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO messages (pet_id, visitor_name, message)
        VALUES (?, ?, ?)
        ''', (pet_id, visitor_name, message))
        self.conn.commit()
    
    def get_messages(self, pet_id):
        """获取宠物的所有留言"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT visitor_name, message, created_at FROM messages 
        WHERE pet_id = ? ORDER BY created_at DESC
        ''', (pet_id,))
        return cursor.fetchall()
    
    def save_reminder(self, pet_id, reminder_type, reminder_date, custom_name=None, custom_description=None):
        """保存纪念日提醒"""
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO reminders (pet_id, reminder_type, reminder_date, custom_name, custom_description)
        VALUES (?, ?, ?, ?, ?)
        ''', (pet_id, reminder_type, reminder_date, custom_name, custom_description))
        self.conn.commit()
    
    def get_reminders(self, pet_id):
        """获取宠物的所有提醒"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT id, reminder_type, reminder_date, custom_name, custom_description, is_active FROM reminders 
        WHERE pet_id = ? ORDER BY reminder_date
        ''', (pet_id,))
        return cursor.fetchall()
    
    def delete_reminder(self, reminder_id):
        """删除指定的提醒"""
        cursor = self.conn.cursor()
        cursor.execute('''
        DELETE FROM reminders WHERE id = ?
        ''', (reminder_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def save_mood_diary(self, pet_id, mood_type, mood_score, diary_content, weather):
        """保存心情日记"""
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO mood_diaries (pet_id, mood_type, mood_score, diary_content, weather)
        VALUES (?, ?, ?, ?, ?)
        ''', (pet_id, mood_type, mood_score, diary_content, weather))
        self.conn.commit()
    
    def get_mood_diaries(self, pet_id, limit=10):
        """获取宠物的心情日记"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT mood_type, mood_score, diary_content, weather, created_at 
        FROM mood_diaries 
        WHERE pet_id = ? 
        ORDER BY created_at DESC 
        LIMIT ?
        ''', (pet_id, limit))
        return cursor.fetchall()
    
    def save_visit_stat(self, memorial_id, visitor_ip, user_agent):
        """保存访问统计"""
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO visit_stats (memorial_id, visitor_ip, user_agent)
        VALUES (?, ?, ?)
        ''', (memorial_id, visitor_ip, user_agent))
        self.conn.commit()
    
    def get_visit_stats(self, memorial_id):
        """获取纪念馆访问统计"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT COUNT(*) as total_visits, 
               COUNT(DISTINCT visitor_ip) as unique_visitors,
               MAX(visit_time) as last_visit
        FROM visit_stats 
        WHERE memorial_id = ?
        ''', (memorial_id,))
        return cursor.fetchone()
    
    def get_pet_by_memorial_id(self, memorial_id):
        """通过纪念馆ID获取宠物信息"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT p.id, p.user_id, p.name, p.species, p.breed, p.color, 
               p.gender, p.birth_date, p.memorial_date, p.weight, 
               p.personality_type, p.status, p.created_at
        FROM pets p
        JOIN memorials m ON p.id = m.pet_id
        WHERE m.id = ?
        ''', (memorial_id,))
        
        result = cursor.fetchone()
        if result:
            return {
                'id': result[0],
                'user_id': result[1],
                'name': result[2],
                'species': result[3],
                'breed': result[4],
                'color': result[5],
                'gender': result[6],
                'birth_date': result[7],
                'memorial_date': result[8],
                'weight': result[9],
                'personality': result[10],  # personality_type 映射为 personality
                'status': result[11],
                'created_at': result[12]
            }
        return None
    
    # 验证码和密码重置相关方法
    def create_email_code(self, email, code_type="verification"):
        """创建邮箱验证码"""
        cursor = self.conn.cursor()
        
        # 生成6位数字验证码
        import random
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        # 设置过期时间（10分钟）
        expires_at = datetime.now() + timedelta(minutes=10)
        
        # 删除该邮箱之前的验证码
        cursor.execute('DELETE FROM email_codes WHERE email = ? AND type = ?', (email, code_type))
        
        # 插入新验证码
        cursor.execute('''
        INSERT INTO email_codes (email, code, code_type, type, expires_at)
        VALUES (?, ?, ?, ?, ?)
        ''', (email, code, code_type, code_type, expires_at))
        
        self.conn.commit()
        return code
    
    def verify_email_code(self, email, code, code_type="verification"):
        """验证邮箱验证码"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
        SELECT id FROM email_codes 
        WHERE email = ? AND code = ? AND type = ? AND expires_at > CURRENT_TIMESTAMP
        ''', (email, code, code_type))
        
        result = cursor.fetchone()
        if result:
            # 验证成功后删除验证码
            cursor.execute('DELETE FROM email_codes WHERE email = ? AND type = ?', (email, code_type))
            self.conn.commit()
            return True
        
        return False
    
    def create_password_reset_token(self, email):
        """创建密码重置令牌"""
        cursor = self.conn.cursor()
        
        # 生成重置令牌
        token = secrets.token_urlsafe(32)
        
        # 设置过期时间（1小时）
        expires_at = datetime.now() + timedelta(hours=1)
        
        # 删除该邮箱之前的重置令牌
        cursor.execute('DELETE FROM password_reset_tokens WHERE email = ?', (email,))
        
        # 插入新令牌
        cursor.execute('''
        INSERT INTO password_reset_tokens (email, token, expires_at)
        VALUES (?, ?, ?)
        ''', (email, token, expires_at))
        
        self.conn.commit()
        return token
    
    def verify_password_reset_token(self, email, token):
        """验证密码重置令牌"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
        SELECT id FROM password_reset_tokens 
        WHERE email = ? AND token = ? AND expires_at > CURRENT_TIMESTAMP AND used = 0
        ''', (email, token))
        
        return cursor.fetchone() is not None
    
    def mark_password_reset_token_used(self, email, token):
        """标记密码重置令牌为已使用"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
        UPDATE password_reset_tokens SET used = 1 
        WHERE email = ? AND token = ?
        ''', (email, token))
        
        self.conn.commit()
    
    def reset_user_password(self, email, new_password):
        """重置用户密码"""
        cursor = self.conn.cursor()
        
        # 生成新的盐值和密码哈希
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((new_password + salt).encode()).hexdigest()
        
        cursor.execute('''
        UPDATE users SET password_hash = ?, salt = ? WHERE email = ?
        ''', (password_hash, salt, email))
        
        self.conn.commit()
        return cursor.rowcount > 0
    
    def user_exists(self, email):
        """检查用户是否存在"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        return cursor.fetchone() is not None
    
    # 充值相关方法
    def create_payment_order(self, user_id: int, order_type: str, amount: float, 
                           payment_method: str = None, description: str = None) -> str:
        """创建支付订单"""
        cursor = self.conn.cursor()
        
        # 生成订单ID
        import uuid
        order_id = str(uuid.uuid4())
        
        # 设置过期时间（30分钟）
        expires_at = datetime.now() + timedelta(minutes=30)
        
        try:
            cursor.execute('''
            INSERT INTO payment_orders (id, user_id, order_type, amount, payment_method, expires_at, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (order_id, user_id, order_type, amount, payment_method, expires_at, description))
            
            self.conn.commit()
            return order_id
        except Exception as e:
            print(f"创建支付订单失败: {e}")
            return None
    
    def get_payment_order(self, order_id: str):
        """获取支付订单信息"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT id, user_id, order_type, amount, currency, payment_method, 
               payment_status, payment_platform, payment_time, created_at, 
               expires_at, description
        FROM payment_orders WHERE id = ?
        ''', (order_id,))
        
        result = cursor.fetchone()
        if result:
            return {
                'id': result[0],
                'user_id': result[1],
                'order_type': result[2],
                'amount': result[3],
                'currency': result[4],
                'payment_method': result[5],
                'payment_status': result[6],
                'payment_platform': result[7],
                'payment_time': result[8],
                'created_at': result[9],
                'expires_at': result[10],
                'description': result[11]
            }
        return None
    
    def update_payment_status(self, order_id: str, status: str, payment_platform: str = None):
        """更新支付状态"""
        cursor = self.conn.cursor()
        
        try:
            if status == 'paid':
                cursor.execute('''
                UPDATE payment_orders 
                SET payment_status = ?, payment_platform = ?, payment_time = CURRENT_TIMESTAMP
                WHERE id = ?
                ''', (status, payment_platform, order_id))
            else:
                cursor.execute('''
                UPDATE payment_orders 
                SET payment_status = ?, payment_platform = ?
                WHERE id = ?
                ''', (status, payment_platform, order_id))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"更新支付状态失败: {e}")
            return False
    
    def get_user_balance(self, user_id: int):
        """获取用户余额"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT balance, frozen_balance, total_recharged, total_consumed
        FROM user_balance WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        if result:
            return {
                'balance': result[0],
                'frozen_balance': result[1],
                'total_recharged': result[2],
                'total_consumed': result[3]
            }
        return None
    
    def init_user_balance(self, user_id: int):
        """初始化用户余额"""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute('''
            INSERT OR IGNORE INTO user_balance (user_id, balance, frozen_balance, total_recharged, total_consumed)
            VALUES (?, 0.0, 0.0, 0.0, 0.0)
            ''', (user_id,))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"初始化用户余额失败: {e}")
            return False
    
    def add_user_balance(self, user_id: int, amount: float, order_id: str, recharge_type: str = 'upgrade'):
        """增加用户余额"""
        cursor = self.conn.cursor()
        
        try:
            # 获取当前余额
            balance_info = self.get_user_balance(user_id)
            if not balance_info:
                self.init_user_balance(user_id)
                balance_info = self.get_user_balance(user_id)
            
            balance_before = balance_info['balance']
            balance_after = balance_before + amount
            
            # 更新余额
            cursor.execute('''
            UPDATE user_balance 
            SET balance = ?, total_recharged = total_recharged + ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
            ''', (balance_after, amount, user_id))
            
            # 记录充值记录
            cursor.execute('''
            INSERT INTO recharge_records (user_id, order_id, amount, balance_before, balance_after, recharge_type)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, order_id, amount, balance_before, balance_after, recharge_type))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"增加用户余额失败: {e}")
            return False
    
    def upgrade_user_level(self, user_id: int, new_level: int, order_id: str = None):
        """升级用户等级"""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute('''
            UPDATE users 
            SET user_level = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            ''', (new_level, user_id))
            
            # 如果有订单ID，记录升级记录
            if order_id:
                cursor.execute('''
                INSERT INTO recharge_records (user_id, order_id, amount, balance_before, balance_after, recharge_type)
                VALUES (?, ?, 0, 0, 0, 'upgrade')
                ''', (user_id, order_id))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"升级用户等级失败: {e}")
            return False
    
    def get_user_payment_orders(self, user_id: int, limit: int = 20):
        """获取用户支付订单列表"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT id, order_type, amount, payment_method, payment_status, 
               payment_time, created_at, description
        FROM payment_orders 
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        ''', (user_id, limit))
        
        results = cursor.fetchall()
        orders = []
        for row in results:
            orders.append({
                'id': row[0],
                'order_type': row[1],
                'amount': row[2],
                'payment_method': row[3],
                'payment_status': row[4],
                'payment_time': row[5],
                'created_at': row[6],
                'description': row[7]
            })
        return orders
    
    def get_memorial_by_id(self, memorial_id: str):
        """根据ID获取纪念馆详情"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT id, pet_id, memorial_url, ai_letter, theme_template, is_public, 
               user_id, pet_name, species, breed, color, gender, birth_date, 
               memorial_date, weight, description, personality, created_at, updated_at
        FROM memorials 
        WHERE id = ?
        ''', (memorial_id,))
        
        result = cursor.fetchone()
        if result:
            return {
                'id': result[0],
                'pet_id': result[1],
                'memorial_url': result[2],
                'ai_letter': result[3],
                'theme_template': result[4],
                'is_public': result[5],
                'user_id': result[6],
                'pet_name': result[7],
                'species': result[8],
                'breed': result[9],
                'color': result[10],
                'gender': result[11],
                'birth_date': result[12],
                'memorial_date': result[13],
                'weight': result[14],
                'description': result[15],
                'personality': result[16],
                'created_at': result[17],
                'updated_at': result[18]
            }
        return None
    
    def update_memorial(self, memorial_id: str, **kwargs):
        """更新纪念馆信息"""
        cursor = self.conn.cursor()
        
        # 构建更新字段
        update_fields = []
        values = []
        
        for key, value in kwargs.items():
            if value is not None:
                update_fields.append(f"{key} = ?")
                values.append(value)
        
        if not update_fields:
            return True
        
        values.append(memorial_id)
        
        try:
            cursor.execute(f'''
            UPDATE memorials 
            SET {', '.join(update_fields)}
            WHERE id = ?
            ''', values)
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"更新纪念馆失败: {e}")
            return False
    
    def delete_memorial(self, memorial_id: str, user_id: int = None):
        """删除纪念馆"""
        cursor = self.conn.cursor()
        
        try:
            # 如果提供了 user_id，先检查纪念馆是否属于该用户
            if user_id is not None:
                cursor.execute('''
                SELECT COUNT(*) FROM user_memorials WHERE memorial_id = ? AND user_id = ?
                ''', (memorial_id, user_id))
                if cursor.fetchone()[0] == 0:
                    return False  # 纪念馆不属于该用户
            
            # 获取宠物ID（在删除前）
            cursor.execute('SELECT pet_id FROM memorials WHERE id = ?', (memorial_id,))
            result = cursor.fetchone()
            pet_id = result[0] if result else None
            
            # 删除相关数据（按依赖关系顺序）
            if pet_id:
                cursor.execute('DELETE FROM personality_tests WHERE pet_id = ?', (pet_id,))
                cursor.execute('DELETE FROM photos WHERE pet_id = ?', (pet_id,))
                cursor.execute('DELETE FROM messages WHERE pet_id = ?', (pet_id,))
            
            # 删除 user_memorials 关联记录（重要：确保纪念馆数量统计正确）
            cursor.execute('DELETE FROM user_memorials WHERE memorial_id = ?', (memorial_id,))
            
            # 删除纪念馆照片
            cursor.execute('DELETE FROM memorial_photos WHERE memorial_id = ?', (memorial_id,))
            
            # 删除纪念馆记录
            cursor.execute('DELETE FROM memorials WHERE id = ?', (memorial_id,))
            
            # 删除关联的宠物记录
            if pet_id:
                cursor.execute('DELETE FROM pets WHERE id = ?', (pet_id,))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"删除纪念馆失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_memorial_photos(self, memorial_id: str):
        """获取纪念馆照片列表"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT photo_url FROM memorial_photos 
        WHERE memorial_id = ? 
        ORDER BY created_at ASC
        ''', (memorial_id,))
        
        results = cursor.fetchall()
        return [result[0] for result in results]
    
    def add_memorial_photo(self, memorial_id: str, photo_url: str):
        """添加纪念馆照片"""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO memorial_photos (memorial_id, photo_url, created_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (memorial_id, photo_url))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"添加纪念馆照片失败: {e}")
            return False
    
    def delete_memorial_photo(self, memorial_id: str, photo_url: str):
        """删除纪念馆照片"""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute('''
            DELETE FROM memorial_photos 
            WHERE memorial_id = ? AND photo_url = ?
            ''', (memorial_id, photo_url))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"删除纪念馆照片失败: {e}")
            return False
    
    def get_memorial_views(self, memorial_id: str):
        """获取纪念馆访问次数"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT views FROM memorial_stats 
        WHERE memorial_id = ?
        ''', (memorial_id,))
        
        result = cursor.fetchone()
        return result[0] if result else 0
    
    def get_memorial_likes(self, memorial_id: str):
        """获取纪念馆点赞次数"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT likes FROM memorial_stats 
        WHERE memorial_id = ?
        ''', (memorial_id,))
        
        result = cursor.fetchone()
        return result[0] if result else 0
    
    def increment_memorial_views(self, memorial_id: str):
        """增加纪念馆访问次数"""
        cursor = self.conn.cursor()
        
        try:
            # 尝试更新现有记录
            cursor.execute('''
            UPDATE memorial_stats 
            SET views = views + 1 
            WHERE memorial_id = ?
            ''', (memorial_id,))
            
            # 如果没有记录，则插入新记录
            if cursor.rowcount == 0:
                cursor.execute('''
                INSERT INTO memorial_stats (memorial_id, views, likes, created_at)
                VALUES (?, 1, 0, CURRENT_TIMESTAMP)
                ''', (memorial_id,))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"增加访问次数失败: {e}")
            return False
    
    def increment_memorial_likes(self, memorial_id: str):
        """增加纪念馆点赞次数"""
        cursor = self.conn.cursor()
        
        try:
            # 尝试更新现有记录
            cursor.execute('''
            UPDATE memorial_stats 
            SET likes = likes + 1 
            WHERE memorial_id = ?
            ''', (memorial_id,))
            
            # 如果没有记录，则插入新记录
            if cursor.rowcount == 0:
                cursor.execute('''
                INSERT INTO memorial_stats (memorial_id, views, likes, created_at)
                VALUES (?, 0, 1, CURRENT_TIMESTAMP)
                ''', (memorial_id,))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"增加点赞次数失败: {e}")
            return False
    
    # ==================== AI对话相关方法 ====================
    
    def save_chat_message(self, memorial_id: str, user_id: int, role: str, content: str):
        """保存AI对话消息"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO ai_chat_messages (memorial_id, user_id, role, content, created_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (memorial_id, user_id, role, content))
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"保存对话消息失败: {e}")
            return None
    
    def get_chat_history(self, memorial_id: str, user_id: int, limit: int = 50):
        """获取对话历史（最近N条）"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT id, role, content, created_at
        FROM ai_chat_messages
        WHERE memorial_id = ? AND user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        ''', (memorial_id, user_id, limit))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'id': row[0],
                'role': row[1],
                'content': row[2],
                'created_at': row[3]
            })
        
        # 返回时按时间正序排列（最旧的在前）
        return list(reversed(messages))
    
    def delete_chat_history(self, memorial_id: str, user_id: int):
        """删除某个纪念馆的所有对话历史"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
            DELETE FROM ai_chat_messages
            WHERE memorial_id = ? AND user_id = ?
            ''', (memorial_id, user_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"删除对话历史失败: {e}")
            return False
    
    def get_chat_count(self, memorial_id: str, user_id: int):
        """获取对话消息数量"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT COUNT(*) FROM ai_chat_messages
        WHERE memorial_id = ? AND user_id = ?
        ''', (memorial_id, user_id))
        return cursor.fetchone()[0]
    
    # ============ 虚拟陪伴相关方法 ============
    
    def save_emotion_record(self, memorial_id: str, user_id: int, emotion: str, 
                           intensity: float, keywords: list, message: str = ""):
        """保存情绪记录"""
        cursor = self.conn.cursor()
        keywords_json = json.dumps(keywords, ensure_ascii=False)
        cursor.execute('''
        INSERT INTO emotion_records (memorial_id, user_id, emotion, intensity, keywords, message)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (memorial_id, user_id, emotion, intensity, keywords_json, message))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_emotion_history(self, memorial_id: str, limit: int = 50, days: int = 30):
        """获取情绪历史记录"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT emotion, intensity, keywords, message, created_at
        FROM emotion_records
        WHERE memorial_id = ? AND created_at >= datetime('now', '-' || ? || ' days')
        ORDER BY created_at DESC
        LIMIT ?
        ''', (memorial_id, days, limit))
        
        records = []
        for row in cursor.fetchall():
            records.append({
                "emotion": row[0],
                "intensity": row[1],
                "keywords": json.loads(row[2]) if row[2] else [],
                "message": row[3],
                "date": row[4]
            })
        return records
    
    def save_greeting_message(self, memorial_id: str, greeting_type: str, content: str):
        """保存问候消息"""
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO greeting_messages (memorial_id, greeting_type, content)
        VALUES (?, ?, ?)
        ''', (memorial_id, greeting_type, content))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_recent_greetings(self, memorial_id: str, limit: int = 10):
        """获取最近的问候消息"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT id, greeting_type, content, is_read, created_at
        FROM greeting_messages
        WHERE memorial_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        ''', (memorial_id, limit))
        
        greetings = []
        for row in cursor.fetchall():
            greetings.append({
                "id": row[0],
                "type": row[1],
                "content": row[2],
                "is_read": row[3],
                "created_at": row[4]
            })
        return greetings
    
    def mark_greeting_as_read(self, greeting_id: int):
        """标记问候消息为已读"""
        cursor = self.conn.cursor()
        cursor.execute('''
        UPDATE greeting_messages SET is_read = 1 WHERE id = ?
        ''', (greeting_id,))
        self.conn.commit()
    
    def get_pet_state(self, memorial_id: str, user_id: int) -> dict:
        """获取宠物状态"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT mood, energy, intimacy, last_interaction
        FROM pet_states
        WHERE memorial_id = ? AND user_id = ?
        ''', (memorial_id, user_id))
        
        row = cursor.fetchone()
        if row:
            return {
                "mood": row[0],
                "energy": row[1],
                "intimacy": row[2],
                "last_interaction": row[3]
            }
        else:
            # 返回默认状态
            return {
                "mood": 70,
                "energy": 60,
                "intimacy": 0,
                "last_interaction": None
            }
    
    def update_pet_state(self, memorial_id: str, user_id: int, state: dict):
        """更新宠物状态"""
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT OR REPLACE INTO pet_states 
        (memorial_id, user_id, mood, energy, intimacy, last_interaction, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        ''', (memorial_id, user_id, state.get("mood", 50), 
              state.get("energy", 50), state.get("intimacy", 0),
              state.get("last_interaction")))
        self.conn.commit()
    
    def record_interaction(self, memorial_id: str, user_id: int, interaction_type: str):
        """记录互动"""
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO interaction_records (memorial_id, user_id, interaction_type)
        VALUES (?, ?, ?)
        ''', (memorial_id, user_id, interaction_type))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_interaction_stats(self, memorial_id: str, user_id: int, days: int = 7):
        """获取互动统计"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT interaction_type, COUNT(*) as count
        FROM interaction_records
        WHERE memorial_id = ? AND user_id = ? 
        AND created_at >= datetime('now', '-' || ? || ' days')
        GROUP BY interaction_type
        ''', (memorial_id, user_id, days))
        
        stats = {}
        for row in cursor.fetchall():
            stats[row[0]] = row[1]
        
        # 总互动次数
        total = sum(stats.values())
        
        return {
            "feed": stats.get("feed", 0),
            "play": stats.get("play", 0),
            "walk": stats.get("walk", 0),
            "pet": stats.get("pet", 0),
            "total": total,
            "days": days
        }
    
    # ==================== 梦境日记相关方法 ====================
    
    def create_dream_diary(self, memorial_id: str, user_id: int, dream_date: str, 
                          dream_content: str, emotion_type: str = None, 
                          mood_score: int = None, tags: str = None, 
                          dream_time: str = None, is_private: bool = False):
        """创建梦境日记"""
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO dream_diaries (memorial_id, user_id, dream_date, dream_time, 
                                   dream_content, emotion_type, mood_score, tags, is_private)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (memorial_id, user_id, dream_date, dream_time, dream_content, 
              emotion_type, mood_score, tags, is_private))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_dream_diaries(self, memorial_id: str, user_id: int = None, limit: int = 50):
        """获取梦境日记列表"""
        cursor = self.conn.cursor()
        if user_id:
            cursor.execute('''
            SELECT id, memorial_id, user_id, dream_date, dream_time, dream_content, 
                   emotion_type, mood_score, tags, ai_analysis, is_private, is_favorite,
                   created_at, updated_at
            FROM dream_diaries 
            WHERE memorial_id = ? AND user_id = ?
            ORDER BY dream_date DESC, created_at DESC
            LIMIT ?
            ''', (memorial_id, user_id, limit))
        else:
            cursor.execute('''
            SELECT id, memorial_id, user_id, dream_date, dream_time, dream_content, 
                   emotion_type, mood_score, tags, ai_analysis, is_private, is_favorite,
                   created_at, updated_at
            FROM dream_diaries 
            WHERE memorial_id = ? AND is_private = 0
            ORDER BY dream_date DESC, created_at DESC
            LIMIT ?
            ''', (memorial_id, limit))
        
        dreams = []
        for row in cursor.fetchall():
            dreams.append({
                'id': row[0],
                'memorial_id': row[1],
                'user_id': row[2],
                'dream_date': row[3],
                'dream_time': row[4],
                'dream_content': row[5],
                'emotion_type': row[6],
                'mood_score': row[7],
                'tags': row[8],
                'ai_analysis': row[9],
                'is_private': row[10],
                'is_favorite': row[11],
                'created_at': row[12],
                'updated_at': row[13]
            })
        return dreams
    
    def get_dream_diary_by_id(self, dream_id: int, user_id: int = None):
        """获取单个梦境日记"""
        cursor = self.conn.cursor()
        if user_id:
            cursor.execute('''
            SELECT id, memorial_id, user_id, dream_date, dream_time, dream_content, 
                   emotion_type, mood_score, tags, ai_analysis, is_private, is_favorite,
                   created_at, updated_at
            FROM dream_diaries 
            WHERE id = ? AND user_id = ?
            ''', (dream_id, user_id))
        else:
            cursor.execute('''
            SELECT id, memorial_id, user_id, dream_date, dream_time, dream_content, 
                   emotion_type, mood_score, tags, ai_analysis, is_private, is_favorite,
                   created_at, updated_at
            FROM dream_diaries 
            WHERE id = ?
            ''', (dream_id,))
        
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'memorial_id': row[1],
                'user_id': row[2],
                'dream_date': row[3],
                'dream_time': row[4],
                'dream_content': row[5],
                'emotion_type': row[6],
                'mood_score': row[7],
                'tags': row[8],
                'ai_analysis': row[9],
                'is_private': row[10],
                'is_favorite': row[11],
                'created_at': row[12],
                'updated_at': row[13]
            }
        return None
    
    def update_dream_diary(self, dream_id: int, user_id: int, **kwargs):
        """更新梦境日记"""
        allowed_fields = ['dream_date', 'dream_time', 'dream_content', 'emotion_type', 
                         'mood_score', 'tags', 'ai_analysis', 'is_private', 'is_favorite']
        
        updates = []
        values = []
        for key, value in kwargs.items():
            if key in allowed_fields:
                updates.append(f"{key} = ?")
                values.append(value)
        
        if not updates:
            return False
        
        # 添加updated_at
        updates.append("updated_at = CURRENT_TIMESTAMP")
        values.extend([dream_id, user_id])
        
        cursor = self.conn.cursor()
        cursor.execute(f'''
        UPDATE dream_diaries 
        SET {", ".join(updates)}
        WHERE id = ? AND user_id = ?
        ''', values)
        self.conn.commit()
        return cursor.rowcount > 0
    
    def delete_dream_diary(self, dream_id: int, user_id: int):
        """删除梦境日记"""
        cursor = self.conn.cursor()
        cursor.execute('''
        DELETE FROM dream_diaries 
        WHERE id = ? AND user_id = ?
        ''', (dream_id, user_id))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def get_dream_stats(self, memorial_id: str, user_id: int):
        """获取梦境统计"""
        cursor = self.conn.cursor()
        
        # 总梦境数
        cursor.execute('''
        SELECT COUNT(*) FROM dream_diaries 
        WHERE memorial_id = ? AND user_id = ?
        ''', (memorial_id, user_id))
        total_dreams = cursor.fetchone()[0]
        
        # 按情绪分类统计
        cursor.execute('''
        SELECT emotion_type, COUNT(*) as count
        FROM dream_diaries 
        WHERE memorial_id = ? AND user_id = ? AND emotion_type IS NOT NULL
        GROUP BY emotion_type
        ''', (memorial_id, user_id))
        emotions = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 最近一次梦到的日期
        cursor.execute('''
        SELECT dream_date FROM dream_diaries 
        WHERE memorial_id = ? AND user_id = ?
        ORDER BY dream_date DESC LIMIT 1
        ''', (memorial_id, user_id))
        last_dream = cursor.fetchone()
        last_dream_date = last_dream[0] if last_dream else None
        
        # 收藏数
        cursor.execute('''
        SELECT COUNT(*) FROM dream_diaries 
        WHERE memorial_id = ? AND user_id = ? AND is_favorite = 1
        ''', (memorial_id, user_id))
        favorite_count = cursor.fetchone()[0]
        
        return {
            'total_dreams': total_dreams,
            'emotions': emotions,
            'last_dream_date': last_dream_date,
            'favorite_count': favorite_count
        }
    
    def get_dream_calendar(self, memorial_id: str, user_id: int, year: int, month: int):
        """获取梦境月历数据"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT dream_date, COUNT(*) as count, GROUP_CONCAT(emotion_type) as emotions
        FROM dream_diaries 
        WHERE memorial_id = ? AND user_id = ? 
        AND strftime('%Y', dream_date) = ? 
        AND strftime('%m', dream_date) = ?
        GROUP BY dream_date
        ''', (memorial_id, user_id, str(year), f"{month:02d}"))
        
        calendar_data = {}
        for row in cursor.fetchall():
            calendar_data[row[0]] = {
                'count': row[1],
                'emotions': row[2].split(',') if row[2] else []
            }
        
        return calendar_data
    
    # ==================== 星空纪念相关方法 ====================
    
    def get_all_public_memorials(self):
        """获取所有公开的纪念馆（用于星空展示）"""
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT id, pet_name, species, memorial_date, created_at, user_id
        FROM memorials
        WHERE is_public = 1
        ORDER BY created_at DESC
        LIMIT 1000
        ''')
        
        memorials = []
        for row in cursor.fetchall():
            memorials.append({
                'id': row[0],
                'pet_name': row[1],
                'species': row[2],
                'memorial_date': row[3],
                'created_at': row[4],
                'user_id': row[5]
            })
        
        return memorials
    
    # ==================== 反馈相关方法 ====================
    
    def save_feedback(self, user_id=None, contact=None, content=None):
        """保存用户反馈"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO feedbacks (user_id, contact, content, status, created_at, updated_at)
            VALUES (?, ?, ?, 'pending', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (user_id, contact, content))
            
            feedback_id = cursor.lastrowid
            self.conn.commit()
            return feedback_id
        except Exception as e:
            print(f"保存反馈失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_feedbacks(self, user_id=None, status=None, limit=50):
        """获取反馈列表"""
        cursor = self.conn.cursor()
        try:
            query = 'SELECT id, user_id, contact, content, status, reply, created_at FROM feedbacks WHERE 1=1'
            params = []
            
            if user_id:
                query += ' AND user_id = ?'
                params.append(user_id)
            
            if status:
                query += ' AND status = ?'
                params.append(status)
            
            query += ' ORDER BY created_at DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            feedbacks = []
            for row in results:
                feedbacks.append({
                    'id': row[0],
                    'user_id': row[1],
                    'contact': row[2],
                    'content': row[3],
                    'status': row[4],
                    'reply': row[5],
                    'created_at': row[6]
                })
            
            return feedbacks
        except Exception as e:
            print(f"获取反馈列表失败: {e}")
            return []
    
    def close(self):
        self.conn.close()

    def get_user_by_openid(self, openid):
        """通过 openid 获取用户信息"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
            SELECT id, email, user_level, is_active, email_verified, openid, nickname, avatar_url, phone
            FROM users WHERE openid = ?
            ''', (openid,))
            user = cursor.fetchone()
            if user:
                return {
                    'id': user[0],
                    'email': user[1],
                    'user_level': user[2],
                    'is_active': user[3],
                    'email_verified': user[4],
                    'openid': user[5],
                    'nickname': user[6],
                    'avatar_url': user[7],
                    'phone': user[8]
                }
            else:
                return None
        except Exception as e:
            print(f"get_user_by_openid error: {e}")
            import traceback
            traceback.print_exc()
            return None