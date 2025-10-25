"""
梦境分析服务
使用AI分析用户记录的梦境内容，提供情感分析和梦境解读
"""

import httpx
import json
from typing import Dict

class DreamAnalysisService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        
    async def analyze_dream(self, dream_content: str, pet_name: str) -> Dict:
        """
        分析梦境内容
        返回情感类型、情感分数和AI解读
        """
        prompt = f"""你是一位温暖的心理咨询师，专门帮助失去宠物的主人理解他们的梦境。

用户梦到了已故的宠物 "{pet_name}"，梦境内容如下：
{dream_content}

请分析这个梦境，并提供：
1. 情感类型（从以下选择一个：温馨、思念、快乐、悲伤、平静、焦虑）
2. 情感强度（1-10分，10分为最强烈）
3. 梦境解读（200字以内，温暖治愈的文字，帮助用户理解这个梦境的意义）

请以JSON格式返回：
{{
  "emotion_type": "情感类型",
  "mood_score": 分数,
  "analysis": "梦境解读文字"
}}

注意：
- 要温暖、共情、治愈
- 不要说"只是梦"这类贬低的话
- 强调梦境是思念和爱的表达
- 如果梦境是快乐的，说明宠物在天堂很幸福
- 如果梦境是悲伤的，表达理解和安慰"""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 500
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content'].strip()
                    
                    # 尝试解析JSON
                    try:
                        # 清理可能的markdown代码块标记
                        if content.startswith('```'):
                            content = content.split('```')[1]
                            if content.startswith('json'):
                                content = content[4:]
                        content = content.strip()
                        
                        analysis_result = json.loads(content)
                        
                        return {
                            'emotion_type': analysis_result.get('emotion_type', '温馨'),
                            'mood_score': int(analysis_result.get('mood_score', 5)),
                            'analysis': analysis_result.get('analysis', '这是一个充满爱与思念的梦境。')
                        }
                    except json.JSONDecodeError:
                        # 如果解析失败，返回默认分析
                        return {
                            'emotion_type': '思念',
                            'mood_score': 5,
                            'analysis': content if len(content) < 500 else content[:500]
                        }
                else:
                    return self._get_default_analysis()
                    
        except Exception as e:
            print(f"AI梦境分析失败: {str(e)}")
            return self._get_default_analysis()
    
    def _get_default_analysis(self) -> Dict:
        """返回默认的分析结果"""
        return {
            'emotion_type': '思念',
            'mood_score': 5,
            'analysis': '能在梦中与TA重逢，说明你们之间的羁绊依然深厚。这个梦境承载着你的思念与爱，TA一定能感受到。'
        }
    
    async def get_healing_words(self, emotion_type: str) -> str:
        """根据情感类型生成治愈话语"""
        healing_words = {
            '温馨': '在梦中与TA温暖相遇，这是爱的延续。愿这份温馨陪伴你每一天。',
            '思念': '思念是爱的另一种形式，TA一直在你心中，从未离开。',
            '快乐': '梦中的快乐是真实的，TA在彩虹桥那边一定过得很好，也希望你幸福。',
            '悲伤': '悲伤是正常的情绪，请允许自己慢慢疗愈。TA会永远爱着你。',
            '平静': '平静是接纳的开始，你正在慢慢学会与回忆和平相处。',
            '焦虑': '焦虑说明你很在意TA，但请相信，TA在天堂一定很安好。'
        }
        return healing_words.get(emotion_type, '每一个关于TA的梦，都是爱的证明。')
    
    def suggest_tags(self, dream_content: str) -> list:
        """根据梦境内容建议标签"""
        tags = []
        
        keywords = {
            '玩耍': ['玩', '跑', '追', '跳', '游戏'],
            '温暖': ['抱', '摸', '亲', '舔', '依偎', '陪'],
            '快乐': ['笑', '开心', '快乐', '高兴', '幸福'],
            '思念': ['想', '念', '找', '寻', '呼唤'],
            '告别': ['再见', '离开', '挥手', '走远'],
            '重逢': ['见面', '相遇', '重逢', '出现'],
            '日常': ['吃', '睡', '散步', '回家'],
            '特殊': ['生日', '节日', '纪念']
        }
        
        for tag, words in keywords.items():
            if any(word in dream_content for word in words):
                tags.append(tag)
        
        return tags if tags else ['日常']

