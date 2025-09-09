import sqlite3
import os
import hashlib
import secrets
from datetime import datetime, timedelta

class Database:
    def __init__(self, db_path="pet_memorials.db"):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()
    
    def _create_tables(self):
        cursor = self.conn.cursor()
        
        # 用户表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
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
            theme_template TEXT DEFAULT 'default',
            is_public BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pet_id) REFERENCES pets(id)
        )
        ''')
        
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
        
        # 初始化用户等级数据
        self._init_user_levels()
        
        self.conn.commit()
    
    def _init_user_levels(self):
        """初始化用户等级数据"""
        cursor = self.conn.cursor()
        
        # 检查是否已存在等级数据
        cursor.execute("SELECT COUNT(*) FROM user_levels")
        if cursor.fetchone()[0] == 0:
            levels = [
                (0, "免费用户", 1, 10, 0, 0, 0, 0.0, 0.0, "基础功能，1个纪念馆，10张照片"),
                (1, "高级用户", 5, 100, 1, 1, 0, 29.9, 299.0, "5个纪念馆，100张照片，AI功能，数据导出"),
                (2, "专业用户", -1, -1, 1, 1, 1, 99.9, 999.0, "无限纪念馆，无限照片，自定义域名，优先客服")
            ]
            
            cursor.executemany('''
            INSERT INTO user_levels (level, name, max_memorials, max_photos, can_use_ai, can_export, can_custom_domain, price_monthly, price_yearly, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', levels)
            
            self.conn.commit()

    # 用户相关方法
    def create_user(self, email, password):
        """创建新用户"""
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
            INSERT INTO users (email, password_hash, salt, email_verification_token, email_verification_expires)
            VALUES (?, ?, ?, ?, ?)
            ''', (email, password_hash, salt, verification_token, verification_expires))
            
            user_id = cursor.lastrowid
            self.conn.commit()
            return {"user_id": user_id, "verification_token": verification_token}
        except Exception as e:
            print(f"创建用户失败: {e}")
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
        expires_at = datetime.now() + timedelta(days=30)  # 30天有效期
        
        cursor.execute('''
        INSERT INTO user_sessions (user_id, session_token, expires_at, ip_address, user_agent)
        VALUES (?, ?, ?, ?, ?)
        ''', (user_id, session_token, expires_at, ip_address, user_agent))
        
        self.conn.commit()
        return session_token
    
    def get_user_by_session(self, session_token):
        """通过会话令牌获取用户信息"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
        SELECT u.id, u.email, u.user_level, u.is_active
        FROM users u
        JOIN user_sessions s ON u.id = s.user_id
        WHERE s.session_token = ? AND s.expires_at > CURRENT_TIMESTAMP
        ''', (session_token,))
        
        user = cursor.fetchone()
        if user:
            return {
                'id': user[0],
                'email': user[1],
                'user_level': user[2],
                'is_active': user[3]
            }
        return None
    
    def get_user_by_id(self, user_id):
        """通过用户ID获取用户信息"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
        SELECT id, email, user_level, is_active
        FROM users 
        WHERE id = ? AND is_active = 1
        ''', (user_id,))
        
        user = cursor.fetchone()
        if user:
            return {
                'id': user[0],
                'email': user[1],
                'user_level': user[2],
                'is_active': user[3]
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
        cursor.execute('''
        SELECT level, name, max_memorials, max_photos, can_use_ai, can_export, can_custom_domain, price_monthly, price_yearly, description
        FROM user_levels WHERE level = ?
        ''', (level,))
        return cursor.fetchone()
    
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
        return cursor.fetchall()
    
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
    
    def delete_memorial(self, memorial_id, user_id):
        """删除纪念馆"""
        cursor = self.conn.cursor()
        
        # 首先检查纪念馆是否属于该用户
        cursor.execute('''
        SELECT COUNT(*) FROM user_memorials WHERE memorial_id = ? AND user_id = ?
        ''', (memorial_id, user_id))
        
        if cursor.fetchone()[0] == 0:
            return False  # 纪念馆不属于该用户
        
        # 获取宠物ID
        cursor.execute('''
        SELECT pet_id FROM memorials WHERE id = ?
        ''', (memorial_id,))
        result = cursor.fetchone()
        if not result:
            return False
        
        pet_id = result[0]
        
        # 删除相关数据（按依赖关系顺序）
        cursor.execute('DELETE FROM personality_tests WHERE pet_id = ?', (pet_id,))
        cursor.execute('DELETE FROM photos WHERE pet_id = ?', (pet_id,))
        cursor.execute('DELETE FROM messages WHERE pet_id = ?', (pet_id,))
        cursor.execute('DELETE FROM user_memorials WHERE memorial_id = ?', (memorial_id,))
        cursor.execute('DELETE FROM memorials WHERE id = ?', (memorial_id,))
        cursor.execute('DELETE FROM pets WHERE id = ?', (pet_id,))
        
        self.conn.commit()
        return True
    
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
    
    def create_memorial_record(self, memorial_id, pet_id, memorial_url, ai_letter=""):
        """创建纪念馆记录"""
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO memorials (id, pet_id, memorial_url, ai_letter)
        VALUES (?, ?, ?, ?)
        ''', (memorial_id, pet_id, memorial_url, ai_letter))
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
        SELECT p.* FROM pets p
        JOIN memorials m ON p.id = m.pet_id
        WHERE m.id = ?
        ''', (memorial_id,))
        return cursor.fetchone()
    
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
        INSERT INTO email_codes (email, code, type, expires_at)
        VALUES (?, ?, ?, ?)
        ''', (email, code, code_type, expires_at))
        
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
    
    def close(self):
        self.conn.close()