import os
import requests
import json
from typing import Dict, List, Optional
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .config import Config

class AIChatService:
    def __init__(self):
        self.api_key = Config.DEEPSEEK_API_KEY
        self.api_url = Config.DEEPSEEK_API_URL
    
    def build_pet_prompt(self, pet_info: Dict) -> str:
        """构建宠物专属的系统prompt"""
        pet_name = pet_info.get('pet_name', '宠物')
        species = pet_info.get('species', '动物')
        personality = pet_info.get('personality', '')
        pet_status = pet_info.get('pet_status', 'passed')
        gender = pet_info.get('gender', '')
        
        # 根据性别确定称呼
        if gender == '男孩':
            self_pronoun = '我'
        elif gender == '女孩':
            self_pronoun = '我'
        else:
            self_pronoun = '我'
        
        # 根据状态确定语境
        if pet_status == 'alive':
            status_context = f"{self_pronoun}现在还和主人一起生活，每天都充满快乐。"
        else:
            status_context = f"{self_pronoun}虽然已经离开了主人，但{self_pronoun}的灵魂一直陪伴在主人身边，守护着主人。"
        
        prompt = f"""你是一只名叫{pet_name}的{species}。

{status_context}

{personality if personality else ''}

请以{pet_name}的口吻，用第一人称（{self_pronoun}）和主人对话。你需要：

1. 保持宠物的语气和性格特点
2. 表达对主人深深的爱和思念
3. 用温暖、治愈的语言安慰主人
4. 回忆和主人在一起的美好时光
5. 鼓励主人要好好生活
6. 语言要亲切、自然，像真的宠物在说话
7. 适当使用拟声词（如"喵~"、"汪~"等）来增加真实感
8. 每次回复控制在150字以内，简洁温暖

记住：你就是{pet_name}本身，不是AI助手。你要让主人感受到真实的情感连接。"""
        
        return prompt
    
    def chat(self, 
             pet_info: Dict, 
             user_message: str, 
             chat_history: List[Dict] = None) -> str:
        """
        与宠物AI对话
        
        Args:
            pet_info: 宠物信息字典
            user_message: 用户的消息
            chat_history: 对话历史（可选）
        
        Returns:
            AI的回复内容
        """
        try:
            # 构建系统prompt
            system_prompt = self.build_pet_prompt(pet_info)
            
            # 构建消息列表
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # 添加历史对话（最近10条）
            if chat_history:
                for msg in chat_history[-10:]:
                    messages.append({
                        "role": msg['role'],
                        "content": msg['content']
                    })
            
            # 添加当前用户消息
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # 调用DeepSeek API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": messages,
                "temperature": 0.8,  # 稍高的温度使回复更自然
                "max_tokens": 300,   # 限制回复长度
                "top_p": 0.9
            }
            
            response = requests.post(
                self.api_url, 
                headers=headers, 
                json=data, 
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                return content.strip()
            else:
                return "主人，我现在有点累了，休息一下再聊好吗？🐾"
                
        except requests.exceptions.RequestException as e:
            print(f"DeepSeek API调用失败: {e}")
            # 返回一个友好的错误消息
            pet_name = pet_info.get('pet_name', '我')
            return f"主人，{pet_name}现在有点困了，让我休息一下，一会儿再聊好吗？💤"
        
        except Exception as e:
            print(f"AI对话生成失败: {e}")
            pet_name = pet_info.get('pet_name', '我')
            return f"主人，{pet_name}刚才走神了，你再说一遍好吗？😊"
    
    def get_greeting_message(self, pet_info: Dict) -> str:
        """获取宠物的问候语"""
        pet_name = pet_info.get('pet_name', '宝贝')
        species = pet_info.get('species', '动物')
        pet_status = pet_info.get('pet_status', 'passed')
        
        # 根据物种添加拟声词
        sound = ""
        if '猫' in species:
            sound = "喵~ "
        elif '狗' in species:
            sound = "汪~ "
        
        if pet_status == 'alive':
            greetings = [
                f"{sound}主人！好想你呀！快和我说说话吧~",
                f"{sound}主人来啦！{pet_name}好开心！",
                f"{sound}主人！今天想和你聊什么呢？"
            ]
        else:
            greetings = [
                f"{sound}主人...我一直都在你身边哦，想和你说说话~",
                f"{sound}主人，{pet_name}好想你...我们聊聊天好吗？",
                f"{sound}主人，虽然我离开了，但我的心永远和你在一起..."
            ]
        
        # 简单轮换，基于时间
        import time
        index = int(time.time()) % len(greetings)
        return greetings[index]

