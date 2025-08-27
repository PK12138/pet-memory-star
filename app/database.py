import sqlite3
import os

class Database:
    def __init__(self, db_path="pet_memorials.db"):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()
    
    def _create_tables(self):
        cursor = self.conn.cursor()
        
        # 宠物基本信息表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS pets (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            species TEXT NOT NULL,
            breed TEXT,
            color TEXT,
            gender TEXT,
            birth_date TEXT,
            memorial_date TEXT,
            weight REAL,
            personality_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 纪念馆表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS memorials (
            id TEXT PRIMARY KEY,
            pet_id TEXT NOT NULL,
            memorial_url TEXT NOT NULL,
            ai_letter TEXT,
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
        


        
        self.conn.commit()
    
    def create_pet_record(self, pet_id, name, species, breed, color, gender, birth_date, memorial_date, weight):
        """创建宠物记录"""
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO pets (id, name, species, breed, color, gender, birth_date, memorial_date, weight)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (pet_id, name, species, breed, color, gender, birth_date, memorial_date, weight))
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
    

    
    def close(self):
        self.conn.close()