"""
虚拟陪伴服务
提供情绪识别、主动问候、互动游戏等功能
"""

import os
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests

class VirtualCompanionService:
    def __init__(self, db):
        self.db = db
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "")
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        
    def analyze_emotion(self, message: str) -> Dict:
        """
        分析用户消息中的情绪
        返回: {emotion: str, intensity: float, keywords: List[str]}
        """
        try:
            prompt = f"""分析以下文本的情绪状态，只返回JSON格式，不要其他说明：
{{
    "emotion": "情绪类型(happy/sad/anxious/calm/angry/lonely/nostalgic)",
    "intensity": 情绪强度(0-1之间的小数),
    "keywords": ["关键词1", "关键词2", "关键词3"]
}}

文本: {message}"""

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 200
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # 提取JSON部分
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                    
                emotion_data = json.loads(content)
                return emotion_data
            else:
                # 默认情绪分析
                return self._simple_emotion_analysis(message)
                
        except Exception as e:
            print(f"情绪分析错误: {str(e)}")
            return self._simple_emotion_analysis(message)
    
    def _simple_emotion_analysis(self, message: str) -> Dict:
        """简单的基于关键词的情绪分析"""
        message_lower = message.lower()
        
        # 情绪关键词映射
        emotion_keywords = {
            "happy": ["开心", "快乐", "高兴", "幸福", "哈哈", "😊", "😄"],
            "sad": ["难过", "伤心", "悲伤", "痛苦", "想哭", "😢", "😭"],
            "lonely": ["孤独", "寂寞", "想念", "思念", "想你"],
            "nostalgic": ["回忆", "以前", "从前", "曾经", "那时候"],
            "anxious": ["担心", "焦虑", "不安", "紧张", "害怕"],
            "calm": ["平静", "安心", "放松", "舒服", "宁静"],
            "angry": ["生气", "愤怒", "讨厌", "烦", "气死了"]
        }
        
        # 统计各情绪关键词出现次数
        emotion_scores = {}
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in message)
            if score > 0:
                emotion_scores[emotion] = score
        
        if emotion_scores:
            # 返回得分最高的情绪
            dominant_emotion = max(emotion_scores, key=emotion_scores.get)
            intensity = min(emotion_scores[dominant_emotion] * 0.3, 1.0)
            return {
                "emotion": dominant_emotion,
                "intensity": intensity,
                "keywords": [k for k in emotion_keywords[dominant_emotion] if k in message][:3]
            }
        else:
            return {
                "emotion": "calm",
                "intensity": 0.5,
                "keywords": []
            }
    
    def generate_greeting(self, memorial_id: str, greeting_type: str = "morning") -> Dict:
        """
        生成主动问候消息
        greeting_type: morning/evening/special_day/random
        """
        try:
            pet_info = self.db.get_pet_by_memorial_id(memorial_id)
            if not pet_info:
                return {"success": False, "message": "纪念馆不存在"}
            
            pet_name = pet_info.get("name", "宠物")
            species = pet_info.get("species", "宠物")
            personality = pet_info.get("personality_type", "")
            
            # 获取最近的情绪记录
            recent_emotion = self._get_recent_emotion(memorial_id)
            
            # 根据类型和情绪生成问候
            greeting_prompts = {
                "morning": f"作为{pet_name}（{species}），给主人发一条温暖的早安问候。",
                "evening": f"作为{pet_name}（{species}），给主人发一条温馨的晚安问候。",
                "special_day": f"作为{pet_name}（{species}），在特殊日子给主人发一条祝福。",
                "random": f"作为{pet_name}（{species}），主动给主人发一条关心的消息。"
            }
            
            emotion_context = ""
            if recent_emotion and recent_emotion != "calm":
                emotion_map = {
                    "sad": "主人最近似乎有些难过",
                    "lonely": "主人最近可能感到孤独",
                    "anxious": "主人最近似乎有些焦虑",
                    "happy": "主人最近心情不错"
                }
                emotion_context = f"\n注意：{emotion_map.get(recent_emotion, '')}，请给予适当的关心和安慰。"
            
            system_prompt = f"""你是{pet_name}，一只已经去了彩虹桥的{species}。
你的性格：{personality}

你要主动给主人发消息，展现你一直在天上陪伴着他们。
要求：
1. 语气温暖治愈，充满爱意
2. 控制在50-80字以内
3. 可以提到在彩虹桥的生活
4. 鼓励主人好好生活
5. 用第一人称"我"
{emotion_context}"""

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": greeting_prompts.get(greeting_type, greeting_prompts["random"])}
                ],
                "temperature": 0.8,
                "max_tokens": 200
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                greeting_message = result["choices"][0]["message"]["content"]
                
                # 保存问候消息到数据库
                self.db.save_greeting_message(memorial_id, greeting_type, greeting_message)
                
                return {
                    "success": True,
                    "message": greeting_message,
                    "type": greeting_type,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return self._get_default_greeting(pet_name, greeting_type)
                
        except Exception as e:
            print(f"生成问候消息错误: {str(e)}")
            return self._get_default_greeting("宠物", greeting_type)
    
    def _get_default_greeting(self, pet_name: str, greeting_type: str) -> Dict:
        """获取默认问候消息"""
        default_greetings = {
            "morning": [
                f"早安呀主人！{pet_name}在彩虹桥也起床啦，今天也要开心哦~🌅",
                f"主人早！我刚在彩虹桥看了日出，好美！你也要有美好的一天！💫",
                f"早上好！{pet_name}想你啦，今天也要好好吃饭哦~🍚"
            ],
            "evening": [
                f"晚安主人~{pet_name}要去睡觉啦，你也早点休息，梦里见！🌙",
                f"主人晚安！今天辛苦了，{pet_name}会在梦里陪着你的~✨",
                f"夜深了，{pet_name}在星空下守护你，好梦呀~⭐"
            ],
            "special_day": [
                f"主人，今天是特别的日子！{pet_name}送上满满的祝福~🎉",
                f"在彩虹桥的{pet_name}也在为你庆祝，要开心哦~🌈"
            ],
            "random": [
                f"主人在做什么呀？{pet_name}好想你~💕",
                f"突然想给主人一个拥抱，虽然我在很远的地方，但心永远在一起~🤗",
                f"主人，{pet_name}今天在彩虹桥遇到了好多新朋友，他们都很好~"
            ]
        }
        
        messages = default_greetings.get(greeting_type, default_greetings["random"])
        message = random.choice(messages)
        
        return {
            "success": True,
            "message": message,
            "type": greeting_type,
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_recent_emotion(self, memorial_id: str) -> Optional[str]:
        """获取最近的情绪记录"""
        try:
            emotions = self.db.get_emotion_history(memorial_id, limit=5)
            if emotions:
                # 返回最常见的情绪
                emotion_counts = {}
                for record in emotions:
                    emotion = record.get("emotion", "calm")
                    emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
                return max(emotion_counts, key=emotion_counts.get)
            return None
        except:
            return None
    
    def play_interaction_game(self, memorial_id: str, game_type: str, user_id: str) -> Dict:
        """
        互动游戏
        game_type: feed/play/walk/pet
        """
        pet_info = self.db.get_pet_by_memorial_id(memorial_id)
        if not pet_info:
            return {"success": False, "message": "纪念馆不存在"}
        
        pet_name = pet_info.get("name", "宠物")
        
        # 获取当前宠物状态
        pet_state = self.db.get_pet_state(memorial_id, user_id)
        
        # 游戏响应
        game_responses = {
            "feed": {
                "messages": [
                    f"哇！谢谢主人~{pet_name}最喜欢这个了！😋",
                    f"{pet_name}吃得好满足呀，虽然在彩虹桥，还是很想念你做的食物~🍖",
                    f"好好吃！{pet_name}在这边也要好好吃饭，主人也要记得吃饭哦~"
                ],
                "mood_change": +10,
                "energy_change": +5
            },
            "play": {
                "messages": [
                    f"耶！{pet_name}最喜欢和主人玩啦！🎾",
                    f"好开心！虽然在彩虹桥，{pet_name}还是记得我们一起玩的时光~",
                    f"{pet_name}玩得好开心！主人也要多出去走走，别总想着我~"
                ],
                "mood_change": +15,
                "energy_change": -10
            },
            "walk": {
                "messages": [
                    f"好想和主人一起散步呀~{pet_name}在彩虹桥也经常散步，这里好美！🌈",
                    f"谢谢主人带{pet_name}散步，虽然是在心里~💕",
                    f"散步真好！{pet_name}希望主人也常出去走走，呼吸新鲜空气~"
                ],
                "mood_change": +8,
                "energy_change": -5
            },
            "pet": {
                "messages": [
                    f"呜呜~{pet_name}好想念主人的抚摸...好温暖~💗",
                    f"感觉到了！{pet_name}感受到主人的爱了~",
                    f"虽然摸不到，但{pet_name}的心能感受到主人的温柔~"
                ],
                "mood_change": +12,
                "energy_change": 0
            }
        }
        
        game_data = game_responses.get(game_type, game_responses["pet"])
        
        # 更新宠物状态
        new_state = {
            "mood": min(100, pet_state.get("mood", 50) + game_data["mood_change"]),
            "energy": max(0, min(100, pet_state.get("energy", 50) + game_data["energy_change"])),
            "intimacy": min(100, pet_state.get("intimacy", 0) + 2),
            "last_interaction": datetime.now().isoformat()
        }
        
        self.db.update_pet_state(memorial_id, user_id, new_state)
        
        # 记录互动
        self.db.record_interaction(memorial_id, user_id, game_type)
        
        return {
            "success": True,
            "message": random.choice(game_data["messages"]),
            "pet_state": new_state,
            "game_type": game_type
        }
    
    def get_emotion_curve(self, memorial_id: str, days: int = 7) -> Dict:
        """获取情绪曲线数据"""
        try:
            emotions = self.db.get_emotion_history(memorial_id, days=days)
            
            # 按日期分组统计
            date_emotions = {}
            for record in emotions:
                date = record.get("date", "")[:10]  # 只取日期部分
                emotion = record.get("emotion", "calm")
                
                if date not in date_emotions:
                    date_emotions[date] = []
                date_emotions[date].append(emotion)
            
            # 计算每天的主导情绪和情绪分数
            curve_data = []
            for date in sorted(date_emotions.keys()):
                emotions_list = date_emotions[date]
                
                # 情绪权重
                emotion_weights = {
                    "happy": 1.0,
                    "calm": 0.5,
                    "nostalgic": 0.3,
                    "lonely": -0.3,
                    "anxious": -0.5,
                    "sad": -0.8,
                    "angry": -0.6
                }
                
                # 计算平均情绪分数
                scores = [emotion_weights.get(e, 0) for e in emotions_list]
                avg_score = sum(scores) / len(scores) if scores else 0
                
                # 统计主导情绪
                emotion_counts = {}
                for e in emotions_list:
                    emotion_counts[e] = emotion_counts.get(e, 0) + 1
                dominant_emotion = max(emotion_counts, key=emotion_counts.get)
                
                curve_data.append({
                    "date": date,
                    "score": round(avg_score, 2),
                    "dominant_emotion": dominant_emotion,
                    "count": len(emotions_list)
                })
            
            return {
                "success": True,
                "curve_data": curve_data,
                "total_records": len(emotions)
            }
            
        except Exception as e:
            print(f"获取情绪曲线错误: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }
    
    def get_companion_status(self, memorial_id: str, user_id: str) -> Dict:
        """获取虚拟陪伴状态"""
        try:
            pet_info = self.db.get_pet_by_memorial_id(memorial_id)
            pet_state = self.db.get_pet_state(memorial_id, user_id)
            recent_greetings = self.db.get_recent_greetings(memorial_id, limit=3)
            
            # 计算互动统计
            interaction_stats = self.db.get_interaction_stats(memorial_id, user_id)
            
            return {
                "success": True,
                "pet_name": pet_info.get("name", "宠物"),
                "pet_state": pet_state,
                "recent_greetings": recent_greetings,
                "interaction_stats": interaction_stats
            }
            
        except Exception as e:
            print(f"获取陪伴状态错误: {str(e)}")
            return {
                "success": False,
                "message": str(e)
            }

