"""
星币系统服务模块
提供星币相关的所有业务逻辑
"""
import json
from datetime import date, datetime, timedelta

class CoinsService:
    """星币系统服务"""
    
    def __init__(self, db):
        """
        初始化星币服务
        :param db: Database实例
        """
        self.db = db
    
    def init_user_coins(self, user_id, initial_balance=100):
        """初始化用户星币账户"""
        cursor = self.db.conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO user_coins (user_id, balance, total_earned)
                VALUES (?, ?, ?)
            ''', (user_id, initial_balance, initial_balance))
            
            # 记录初始奖励
            cursor.execute('''
                INSERT INTO coin_transactions (user_id, amount, type, description)
                VALUES (?, ?, ?, ?)
            ''', (user_id, initial_balance, 'new_user_reward', '新用户福利'))
            
            self.db.conn.commit()
            return True
        except Exception as e:
            print(f"初始化星币账户失败: {e}")
            return False
    
    def get_user_coins(self, user_id):
        """获取用户星币余额"""
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT balance, total_earned, total_spent, created_at, updated_at
            FROM user_coins WHERE user_id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        
        if result:
            return {
                'balance': result[0],
                'total_earned': result[1],
                'total_spent': result[2],
                'created_at': result[3],
                'updated_at': result[4]
            }
        else:
            # 如果用户还没有星币账户，初始化一个
            self.init_user_coins(user_id)
            return self.get_user_coins(user_id)
    
    def add_coins(self, user_id, amount, coin_type, description, metadata=None):
        """增加用户星币"""
        cursor = self.db.conn.cursor()
        try:
            # 更新余额和累计获得
            cursor.execute('''
                UPDATE user_coins 
                SET balance = balance + ?,
                    total_earned = total_earned + ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (amount, amount, user_id))
            
            # 记录交易
            metadata_str = json.dumps(metadata) if metadata else None
            cursor.execute('''
                INSERT INTO coin_transactions (user_id, amount, type, description, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, amount, coin_type, description, metadata_str))
            
            self.db.conn.commit()
            
            # 返回新余额
            new_balance = self.get_user_coins(user_id)['balance']
            return True, new_balance
        except Exception as e:
            self.db.conn.rollback()
            return False, str(e)
    
    def spend_coins(self, user_id, amount, coin_type, description, metadata=None):
        """消费用户星币"""
        cursor = self.db.conn.cursor()
        
        # 检查余额是否足够
        coins_info = self.get_user_coins(user_id)
        if coins_info['balance'] < amount:
            return False, "星币余额不足"
        
        try:
            # 更新余额和累计消费
            cursor.execute('''
                UPDATE user_coins 
                SET balance = balance - ?,
                    total_spent = total_spent + ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (amount, amount, user_id))
            
            # 记录交易（负数表示消费）
            metadata_str = json.dumps(metadata) if metadata else None
            cursor.execute('''
                INSERT INTO coin_transactions (user_id, amount, type, description, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, -amount, coin_type, description, metadata_str))
            
            self.db.conn.commit()
            
            # 返回新余额
            new_balance = self.get_user_coins(user_id)['balance']
            return True, new_balance
        except Exception as e:
            self.db.conn.rollback()
            return False, str(e)
    
    def get_coin_transactions(self, user_id, limit=20, offset=0, transaction_type=None):
        """获取星币交易记录"""
        cursor = self.db.conn.cursor()
        
        if transaction_type:
            cursor.execute('''
                SELECT id, amount, type, description, metadata, created_at
                FROM coin_transactions
                WHERE user_id = ? AND type = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            ''', (user_id, transaction_type, limit, offset))
        else:
            cursor.execute('''
                SELECT id, amount, type, description, metadata, created_at
                FROM coin_transactions
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            ''', (user_id, limit, offset))
        
        rows = cursor.fetchall()
        transactions = []
        for row in rows:
            transactions.append({
                'id': row[0],
                'amount': row[1],
                'type': row[2],
                'description': row[3],
                'metadata': json.loads(row[4]) if row[4] else None,
                'created_at': row[5]
            })
        
        # 获取总数
        if transaction_type:
            cursor.execute('SELECT COUNT(*) FROM coin_transactions WHERE user_id = ? AND type = ?', 
                         (user_id, transaction_type))
        else:
            cursor.execute('SELECT COUNT(*) FROM coin_transactions WHERE user_id = ?', (user_id,))
        
        total = cursor.fetchone()[0]
        
        return transactions, total
    
    def daily_sign_in(self, user_id):
        """每日签到"""
        cursor = self.db.conn.cursor()
        today = date.today().isoformat()
        
        # 检查今天是否已签到
        cursor.execute('''
            SELECT id FROM daily_sign_in 
            WHERE user_id = ? AND sign_date = ?
        ''', (user_id, today))
        
        if cursor.fetchone():
            return False, "今日已签到", 0
        
        # 获取最近的签到记录，计算连续天数
        cursor.execute('''
            SELECT sign_date, continuous_days 
            FROM daily_sign_in 
            WHERE user_id = ?
            ORDER BY sign_date DESC LIMIT 1
        ''', (user_id,))
        
        last_sign = cursor.fetchone()
        continuous_days = 1
        
        if last_sign:
            last_date = datetime.strptime(last_sign[0], '%Y-%m-%d').date()
            yesterday = date.today() - timedelta(days=1)
            
            if last_date == yesterday:
                # 连续签到
                continuous_days = last_sign[1] + 1
        
        # 计算奖励（基础10星币，连续签到有额外奖励）
        reward = 10
        if continuous_days == 7:
            reward = 50  # 周奖励
        elif continuous_days == 14:
            reward = 100
        elif continuous_days == 30:
            reward = 300  # 月度大奖
        
        try:
            # 记录签到
            cursor.execute('''
                INSERT INTO daily_sign_in (user_id, sign_date, continuous_days, reward_coins)
                VALUES (?, ?, ?, ?)
            ''', (user_id, today, continuous_days, reward))
            
            # 增加星币
            self.add_coins(user_id, reward, 'sign_in', f'每日签到（连续{continuous_days}天）')
            
            self.db.conn.commit()
            return True, {
                'reward': reward,
                'continuous_days': continuous_days,
                'message': f'签到成功！连续签到{continuous_days}天，获得{reward}星币'
            }, reward
        except Exception as e:
            self.db.conn.rollback()
            print(f"签到失败: {e}")
            return False, str(e), 0
    
    def complete_task(self, user_id, task_type, reward_coins, max_daily_count=None):
        """完成任务获得星币"""
        cursor = self.db.conn.cursor()
        today = date.today().isoformat()
        
        # 检查今天完成次数
        cursor.execute('''
            SELECT completion_count FROM task_completions
            WHERE user_id = ? AND task_type = ? AND completion_date = ?
        ''', (user_id, task_type, today))
        
        result = cursor.fetchone()
        today_count = result[0] if result else 0
        
        # 检查是否超过每日限制
        if max_daily_count and today_count >= max_daily_count:
            return False, f'今日任务次数已达上限', today_count
        
        try:
            if result:
                # 更新今日完成次数
                cursor.execute('''
                    UPDATE task_completions
                    SET completion_count = completion_count + 1,
                        reward_coins = reward_coins + ?
                    WHERE user_id = ? AND task_type = ? AND completion_date = ?
                ''', (reward_coins, user_id, task_type, today))
            else:
                # 首次完成
                cursor.execute('''
                    INSERT INTO task_completions (user_id, task_type, completion_date, reward_coins)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, task_type, today, reward_coins))
            
            # 增加星币
            task_names = {
                'upload_photo': '上传照片',
                'write_text': '撰写纪念文字',
                'ai_chat': 'AI对话',
                'dream_diary': '记录梦境',
                'mood_diary': '记录心情'
            }
            task_name = task_names.get(task_type, task_type)
            self.add_coins(user_id, reward_coins, f'task_{task_type}', task_name)
            
            self.db.conn.commit()
            return True, f'完成{task_name}，获得{reward_coins}星币', today_count + 1
        except Exception as e:
            self.db.conn.rollback()
            print(f"任务完成失败: {e}")
            return False, str(e), today_count
    
    def watch_ad(self, user_id, ad_unit_id, reward_coins=50, max_daily_count=5):
        """观看激励视频广告"""
        cursor = self.db.conn.cursor()
        today = date.today().isoformat()
        
        # 检查今天观看次数
        cursor.execute('''
            SELECT view_count FROM ad_views
            WHERE user_id = ? AND view_date = ?
        ''', (user_id, today))
        
        result = cursor.fetchone()
        today_count = result[0] if result else 0
        
        # 检查是否超过每日限制
        if today_count >= max_daily_count:
            return False, '今日观看广告次数已达上限', today_count
        
        try:
            if result:
                # 更新今日观看次数
                cursor.execute('''
                    UPDATE ad_views
                    SET view_count = view_count + 1,
                        reward_coins = reward_coins + ?
                    WHERE user_id = ? AND view_date = ?
                ''', (reward_coins, user_id, today))
            else:
                # 首次观看
                cursor.execute('''
                    INSERT INTO ad_views (user_id, ad_unit_id, view_date, reward_coins)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, ad_unit_id, today, reward_coins))
            
            # 增加星币
            self.add_coins(user_id, reward_coins, 'watch_ad', '观看激励视频广告', 
                         {'ad_unit_id': ad_unit_id})
            
            self.db.conn.commit()
            return True, f'观看广告成功，获得{reward_coins}星币', today_count + 1
        except Exception as e:
            self.db.conn.rollback()
            print(f"广告观看失败: {e}")
            return False, str(e), today_count
    
    # 任务奖励配置
    TASK_REWARDS = {
        'upload_photo': {'reward': 5, 'max_daily': 3},
        'write_text': {'reward': 20, 'max_daily': 2},
        'ai_chat': {'reward': 2, 'max_daily': 10},
        'dream_diary': {'reward': 15, 'max_daily': 2},
        'mood_diary': {'reward': 15, 'max_daily': 2},
    }


