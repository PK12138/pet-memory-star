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
        # 分析性格测试答案，提取个性化特征
        personality_traits = self._analyze_personality_traits(answers)
        
        # 基于品种和毛色生成特色描述
        species_traits = self._get_species_traits(pet_info.get('species', ''))
        color_traits = self._get_color_traits(pet_info.get('color', ''))
        
        prompt = f"""
        请以{pet_info['name']}（一只{pet_info['species']}）的身份，写一封独特而感人的信给主人。

        宠物详细信息：
        - 名字：{pet_info['name']}
        - 品种：{pet_info.get('breed', '未知')}
        - 毛色：{pet_info.get('color', '未知')} {color_traits}
        - 性别：{pet_info.get('gender', '未知')}
        - 性格类型：{personality_type}
        - 性格特征：{personality_traits}
        - 品种特点：{species_traits}

        性格测试详细答案：{answers}

        请根据以上信息，写一封完全个性化的信件，要求：

        1. 语言风格要完全符合{personality_type}的性格特点
        2. 融入{species_traits}的独特行为描述
        3. 体现{color_traits}的视觉特征
        4. 基于性格测试答案{answers}，展现{pet_info['name']}独特的个性
        5. 回忆要具体、生动，避免模板化表达
        6. 情感要真挚、温暖，但不要过于悲伤
        7. 长度控制在400-600字
        8. 要有独特的开头和结尾，避免千篇一律

        请确保这封信是{pet_info['name']}专属的，与其他宠物的信完全不同。要体现{pet_info['name']}作为{pet_info['species']}的独特魅力和与主人的特殊情感联系。
        """
        return prompt
    
    def _analyze_personality_traits(self, answers: Dict[int, str]) -> str:
        """分析性格测试答案，提取个性化特征"""
        traits = []
        
        # 分析各种性格倾向
        social_count = sum(1 for answer in answers.values() if answer in ['A', 'B'])
        independent_count = sum(1 for answer in answers.values() if answer in ['C', 'D'])
        active_count = sum(1 for answer in answers.values() if answer in ['A', 'C'])
        calm_count = sum(1 for answer in answers.values() if answer in ['B', 'D'])
        
        if social_count > independent_count:
            traits.append("社交性强，喜欢与人互动")
        else:
            traits.append("相对独立，有自己的小世界")
            
        if active_count > calm_count:
            traits.append("活泼好动，充满活力")
        else:
            traits.append("安静温和，喜欢安静时光")
        
        # 分析具体答案模式
        if answers.get(1) == 'A':
            traits.append("对新环境充满好奇")
        elif answers.get(1) == 'D':
            traits.append("对新环境需要时间适应")
            
        if answers.get(3) == 'A':
            traits.append("喜欢主动表达爱意")
        elif answers.get(3) == 'D':
            traits.append("用安静的方式表达爱")
            
        if answers.get(5) == 'A':
            traits.append("情绪表达丰富")
        elif answers.get(5) == 'D':
            traits.append("情绪内敛深沉")
        
        return "，".join(traits)
    
    def _get_species_traits(self, species: str) -> str:
        """获取品种特色描述"""
        species_traits = {
            "猫": "优雅独立，喜欢高处观察，有独特的呼噜声表达满足，会用身体蹭人表达爱意",
            "狗": "忠诚热情，喜欢摇尾巴表达快乐，会叼玩具分享，对主人回家特别兴奋",
            "兔子": "温顺可爱，喜欢蹦跳表达快乐，会用小鼻子轻触主人，安静时喜欢依偎",
            "仓鼠": "小巧活泼，喜欢在轮子上奔跑，会在主人手心里安心睡觉",
            "鸟": "聪明机灵，会模仿声音，喜欢站在主人肩膀上，用翅膀轻抚表达爱意",
            "其他": "有着独特的个性和表达方式"
        }
        return species_traits.get(species, species_traits["其他"])
    
    def _get_color_traits(self, color: str) -> str:
        """获取毛色特色描述"""
        color_traits = {
            "白色": "如雪花般纯洁美丽",
            "黑色": "如夜空般神秘深邃", 
            "棕色": "如巧克力般温暖甜蜜",
            "橙色": "如夕阳般温暖明亮",
            "灰色": "如云朵般柔软优雅",
            "花色": "有着独特的美丽花纹",
            "金色": "如阳光般闪闪发光",
            "银色": "如月光般优雅神秘",
            "黄色": "如小太阳般温暖明亮"
        }
        return color_traits.get(color, "有着独特的美丽")
    
    def _generate_template_letter(self, pet_info: Dict, personality_type: str, answers: Dict[int, str]) -> str:
        """生成模板信件（当AI服务不可用时使用）"""
        personality_descriptions = {
            "内向谨慎型": "虽然我不太善于表达，但我的心一直和你在一起。",
            "外向友好型": "我总是那么活泼，希望能给你带来更多快乐！",
            "敏感依赖型": "我能感受到你的每一个情绪，就像你能感受到我一样。",
            "独立自主型": "虽然我有时很独立，但我的心永远属于你。"
        }
        
        # 基于宠物信息生成个性化内容
        import random
        import hashlib
        import time
        
        # 使用宠物信息和当前时间创建种子，确保每次生成都不同但可控
        seed_str = f"{pet_info.get('name', '')}{pet_info.get('species', '')}{pet_info.get('breed', '')}{pet_info.get('color', '')}{personality_type}{int(time.time())}"
        seed = int(hashlib.md5(seed_str.encode()).hexdigest(), 16) % (2**32)
        random.seed(seed)
        
        # 性格化的开头段落
        personality_openings = {
            "内向谨慎型": [
                "虽然我平时不太爱表达，但今天我想对你说说心里话。我一直在角落里默默观察着你，用我自己的方式爱着你。",
                "我知道我有时候很安静，但我的心里装着满满的爱。每一次你轻抚我的时候，我都能感受到你的温柔。",
                "也许我不是最活泼的小家伙，但我用我独特的方式深深地爱着你，那种爱比任何言语都要真实。"
            ],
            "外向友好型": [
                "嗨！我最亲爱的主人！你知道我有多爱和你玩耍吗？每一天都是我们的冒险日！",
                "我总是那个最爱撒娇、最爱粘着你的小家伙！还记得我每天都要缠着你陪我玩的样子吗？",
                "我是你最活泼的小伙伴！每次看到你回家，我都兴奋得不得了，因为又可以和你一起快乐了！"
            ],
            "敏感依赖型": [
                "我能感受到你内心的每一丝情感，就像你总能读懂我的心思一样。我们之间的默契是那么特别。",
                "你的每一个眼神，每一次抚摸，都深深印在我的心里。我们的心灵连接是如此深刻。",
                "我总是能察觉到你的情绪变化，当你开心时我也开心，当你难过时我会默默陪伴。"
            ],
            "独立自主型": [
                "虽然我总是表现得很独立，但你知道吗？你就是我心中最重要的存在。",
                "我可能不常主动粘着你，但那并不意味着我不需要你。我用我自己的方式深深地依恋着你。",
                "我喜欢保持一点距离，但我的心从未远离过你。你是我选择信任和依靠的唯一。"
            ]
        }
        
        # 基于品种的特色回忆
        species_memories = {
            "猫": [
                "还记得我蜷缩在你腿上打呼噜的午后吗？那是我最安心的时光。",
                "我喜欢在窗台上晒太阳，但更喜欢你在身边的感觉。",
                "每次你回家，我都会优雅地走过来蹭蹭你，那是我表达思念的方式。"
            ],
            "狗": [
                "还记得我每天在门口等你回家，摇着尾巴迎接你的样子吗？",
                "我们一起散步的时光是我最快乐的记忆，我总是兴奋地跑在你前面。",
                "我会把我最喜欢的玩具叼给你，因为我想和你分享我最珍贵的东西。"
            ],
            "兔子": [
                "我最喜欢蹦蹦跳跳地围着你转圈，那是我在向你表达快乐。",
                "当我用小鼻子轻触你的手时，我在告诉你我有多爱你。",
                "安静地依偎在你怀里是我最幸福的时刻。"
            ],
            "其他": [
                "我们一起度过的每个安静的时光都是我最珍贵的回忆。",
                "你总是那么耐心地照顾我，理解我的每一个小习惯。",
                "我用我独特的方式表达着对你的爱，希望你能感受到。"
            ]
        }
        
        # 基于毛色的诗意描述
        color_descriptions = {
            "白色": "雪花般纯洁的我", "黑色": "如夜空般神秘的我", "棕色": "像巧克力一样甜蜜的我",
            "橙色": "如夕阳般温暖的我", "灰色": "像云朵一样柔软的我", "花色": "有着独特花纹的我",
            "金色": "闪闪发光的我", "银色": "如月光般优雅的我", "黄色": "像小太阳一样的我"
        }
        
        # 随机选择内容元素
        opening = random.choice(personality_openings.get(personality_type, ["我想对你说说心里话"]))
        species = pet_info.get('species', '小动物')
        memory = random.choice(species_memories.get(species, species_memories["其他"]))
        color = pet_info.get('color', '')
        color_desc = color_descriptions.get(color, "独一无二的我") if color else "特别的我"
        
        # 随机选择结尾段落
        endings = [
            "在彩虹桥这边，我每天都在想念你。这里很美，但没有你在身边，再美的地方也不完整。我会在这里耐心等待，直到我们再次相遇的那一天。",
            "我会在天上的每一颗星星里守护你，在每一缕阳光中拥抱你。虽然我们暂时分别了，但我们的爱永远连接着彼此的心。",
            "我希望你记住我们在一起时的快乐，而不是分别的悲伤。因为真正的爱是永恒的，我们的爱也会永远存在。",
            "请你一定要好好照顾自己，就像你曾经那么用心地照顾我一样。当你想念我的时候，就看看天空，我一定在那里看着你。"
        ]
        
        ending = random.choice(endings)
        
        # 随机选择温馨的细节
        sweet_details = [
            f"你知道吗？{color_desc}，在你眼中总是最美的。",
            f"作为一只{species}，能遇到你是我这辈子最大的幸运。",
            "你为我准备的每一餐，给我的每一个拥抱，都是我最珍贵的宝藏。",
            "我们一起度过的每个平凡的日子，现在想来都闪闪发光。"
        ]
        
        detail = random.choice(sweet_details)
        
        letter = f"""亲爱的主人：

{opening}

{memory}

{detail}

{ending}

请记住，无论何时何地，我都是你最爱的{pet_info['name']}，你也永远是我心中最重要的人。我们的爱超越了生死，超越了时间，永远不会消失。

带着满满的爱和思念，
你永远的{pet_info['name']} ❤️"""
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
