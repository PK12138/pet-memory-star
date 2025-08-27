import os
import requests
import json
from typing import Dict, List
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

class PersonalityService:
    def __init__(self):
        # 性格测试问题定义
        self.questions = {
            1: "当遇到陌生人时，你的宠物通常会：",
            2: "在玩耍时，你的宠物更喜欢：",
            3: "当主人回家时，你的宠物会：",
            4: "面对新玩具时，你的宠物会：",
            5: "在休息时，你的宠物喜欢：",
            6: "当听到奇怪声音时，你的宠物会：",
            7: "与其他宠物相处时，你的宠物：",
            8: "在训练时，你的宠物：",
            9: "当主人心情不好时，你的宠物会：",
            10: "面对食物时，你的宠物："
        }
        
        # 答案选项
        self.answer_options = {
            1: {
                "A": "躲起来观察",
                "B": "主动上前打招呼",
                "C": "保持距离但好奇",
                "D": "完全不在意"
            },
            2: {
                "A": "独自探索",
                "B": "与主人互动",
                "C": "与其他宠物玩耍",
                "D": "安静地观察"
            },
            3: {
                "A": "兴奋地跑来跑去",
                "B": "温柔地蹭主人",
                "C": "摇尾巴表示欢迎",
                "D": "继续做自己的事"
            },
            4: {
                "A": "立即尝试",
                "B": "先观察再尝试",
                "C": "等主人示范",
                "D": "不感兴趣"
            },
            5: {
                "A": "找个安静角落",
                "B": "靠近主人身边",
                "C": "在能看到主人的地方",
                "D": "随意找个地方"
            },
            6: {
                "A": "立即警觉",
                "B": "好奇地寻找声源",
                "C": "寻求主人保护",
                "D": "继续休息"
            },
            7: {
                "A": "保持独立",
                "B": "主动社交",
                "C": "谨慎接触",
                "D": "完全忽视"
            },
            8: {
                "A": "专注且快速学习",
                "B": "需要鼓励和奖励",
                "C": "容易分心",
                "D": "抗拒训练"
            },
            9: {
                "A": "默默陪伴",
                "B": "主动安慰",
                "C": "试图转移注意力",
                "D": "保持距离"
            },
            10: {
                "A": "立即吃完",
                "B": "慢慢品尝",
                "C": "先闻再吃",
                "D": "挑食"
            }
        }
        
        # 性格类型定义
        self.personality_types = {
            "A": "内向谨慎型",
            "B": "外向友好型", 
            "C": "敏感依赖型",
            "D": "独立自主型"
        }
    
    def get_questions(self) -> Dict[int, str]:
        """获取所有问题"""
        return self.questions
    
    def get_answer_options(self, question_id: int) -> Dict[str, str]:
        """获取指定问题的答案选项"""
        return self.answer_options.get(question_id, {})
    
    def analyze_personality(self, answers: Dict[int, str]) -> str:
        """分析性格类型"""
        if not answers:
            return "未知"
        
        # 统计各选项的数量
        option_counts = {"A": 0, "B": 0, "C": 0, "D": 0}
        for answer in answers.values():
            if answer in option_counts:
                option_counts[answer] += 1
        
        # 找出最多的选项
        dominant_option = max(option_counts, key=option_counts.get)
        return self.personality_types.get(dominant_option, "未知")
    
    def get_personality_description(self, personality_type: str) -> str:
        """获取性格类型描述"""
        descriptions = {
            "内向谨慎型": "你的宠物是一个深思熟虑的小家伙，喜欢观察和思考。它们可能不会立即表达情感，但内心非常细腻。它们需要时间来建立信任，一旦信任建立，就会成为最忠诚的伙伴。",
            "外向友好型": "你的宠物是一个天生的社交达人！它们热情、开朗，喜欢与人和动物互动。它们总是能给周围的人带来快乐，是真正的开心果。",
            "敏感依赖型": "你的宠物非常敏感和依赖，它们能敏锐地感知主人的情绪变化。它们需要更多的关爱和关注，但也会给予最温暖的陪伴。",
            "独立自主型": "你的宠物是一个独立的小个体，它们有自己的想法和节奏。虽然可能不会总是粘着主人，但它们的独立精神让人敬佩。"
        }
        return descriptions.get(personality_type, "这是一个独特的性格类型。")
    
    def _call_deepseek_api(self, prompt: str) -> str:
        """调用DeepSeek API生成AI信件"""
        try:
            # 从配置文件读取DeepSeek API配置
            api_key = Config.DEEPSEEK_API_KEY
            api_url = Config.DEEPSEEK_API_URL
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的宠物情感表达专家，擅长以宠物的身份写温暖感人的信件。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.7,
                "top_p": 0.9
            }
            
            response = requests.post(api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                return content.strip()
            else:
                raise Exception("API响应格式错误")
                
        except requests.exceptions.RequestException as e:
            print(f"网络请求错误: {e}")
            raise Exception(f"网络请求失败: {e}")
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            raise Exception(f"响应解析失败: {e}")
        except Exception as e:
            print(f"DeepSeek API调用异常: {e}")
            raise Exception(f"API调用失败: {e}")
    
    def generate_ai_letter(self, pet_info: Dict, personality_type: str, answers: Dict[int, str]) -> str:
        """使用DeepSeek生成AI信件"""
        try:
            # 构建提示词
            prompt = self._build_letter_prompt(pet_info, personality_type, answers)
            
            # 尝试调用DeepSeek API
            try:
                return self._call_deepseek_api(prompt)
            except Exception as api_error:
                print(f"DeepSeek API调用失败: {api_error}")
                # 如果API调用失败，返回模板信件
                return self._generate_template_letter(pet_info, personality_type, answers)
            
        except Exception as e:
            print(f"AI信件生成失败: {e}")
            return self._generate_fallback_letter(pet_info, personality_type)
    
    def _build_letter_prompt(self, pet_info: Dict, personality_type: str, answers: Dict[int, str]) -> str:
        """构建AI提示词"""
        prompt = f"""
        请以{pet_info['name']}（一只{pet_info['species']}）的身份，写一封信给主人。
        
        宠物信息：
        - 名字：{pet_info['name']}
        - 品种：{pet_info.get('breed', '未知')}
        - 毛色：{pet_info.get('color', '未知')}
        - 性别：{pet_info.get('gender', '未知')}
        - 性格类型：{personality_type}
        
        性格测试答案：{answers}
        
        请写一封温暖、感人的信，表达：
        1. 对主人的感谢和爱
        2. 回忆一起度过的美好时光
        3. 对主人的安慰和鼓励
        4. 希望主人在没有自己的日子里也要快乐
        5. 表达永远的爱和陪伴
        
        要求：语言要温暖、真诚，符合宠物的性格特点，长度在300-500字左右。
        """
        return prompt
    
    def _generate_template_letter(self, pet_info: Dict, personality_type: str, answers: Dict[int, str]) -> str:
        """生成模板信件（当AI服务不可用时使用）"""
        personality_descriptions = {
            "内向谨慎型": "虽然我不太善于表达，但我的心一直和你在一起。",
            "外向友好型": "我总是那么活泼，希望能给你带来更多快乐！",
            "敏感依赖型": "我能感受到你的每一个情绪，就像你能感受到我一样。",
            "独立自主型": "虽然我有时很独立，但我的心永远属于你。"
        }
        
        letter = f"""
亲爱的{pet_info['name']}的主人：

当你看到这封信的时候，我已经在彩虹桥的那一边了。但请相信，我的心永远和你在一起。

{personality_descriptions.get(personality_type, "我们之间的感情是那么特别。")}

还记得我们第一次见面的时候吗？那时的我可能还很小，但我知道你就是我一直在等待的那个人。我们一起度过了那么多美好的时光，每一个瞬间都深深地印在我的心里。

你教会了我什么是爱，什么是家。虽然我只是一只{pet_info['species']}，但我知道你对我的爱是那么真实，那么深沉。我也用我全部的爱回报着你。

现在我要离开了，但请不要为我难过。我在彩虹桥这边过得很好，这里有温暖的阳光，有美丽的花园，还有其他的小动物朋友。我会在这里等你，直到我们再次相见的那一天。

请你一定要快乐，要继续你的生活。我知道你是一个坚强的人，你一定能够度过这个难关。记住，我永远爱你，永远感谢你给了我一个温暖的家。

如果有一天你感到孤单，请抬头看看天空，我会在那里看着你，守护着你。

永远爱你的{pet_info['name']}
        """
        return letter.strip()
    
    def _generate_fallback_letter(self, pet_info: Dict, personality_type: str) -> str:
        """生成备用信件"""
        return f"""
亲爱的{pet_info['name']}的主人：

虽然我无法生成完整的AI信件，但我想告诉你，{pet_info['name']}一定非常爱你。

作为一只{pet_info['species']}，它用自己独特的方式表达着对你的爱。它的离开让这个世界少了一份温暖，但它在天堂里会继续守护着你。

请记住你们之间的美好回忆，让这些回忆成为你前进的力量。

永远爱你的{pet_info['name']}
        """.strip()
