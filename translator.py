"""
OpenAI API Translator Module
调用 OpenAI 兼容 API 进行中译英翻译
"""

import json
from openai import OpenAI


class Translator:
    """翻译器类，封装 OpenAI API 调用"""
    
    def __init__(self, config_path: str = "config.json"):
        """初始化翻译器
        
        Args:
            config_path: 配置文件路径
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        self.client = OpenAI(
            api_key=config['api_key'],
            base_url=config['api_base']
        )
        self.model = config.get('model', 'gpt-3.5-turbo')
        
        self.system_prompt = """你是一个专业的中英翻译专家。请将用户输入的中文翻译成自然流畅的英文。

翻译要求：
1. 保持原文的语气和风格
2. 译文要地道自然，符合英语表达习惯
3. 如果是口语化的中文，翻译成口语化的英文
4. 如果是正式的中文，翻译成正式的英文
5. 只输出翻译结果，不要添加任何解释

注意：用户输入可能是从键盘实时捕获的，可能有一些拼写错误或不完整的句子，请尽量理解其意图并翻译。"""

    def translate(self, chinese_text: str) -> str:
        """翻译中文到英文
        
        Args:
            chinese_text: 待翻译的中文文本
            
        Returns:
            翻译后的英文文本
        """
        if not chinese_text.strip():
            return ""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": chinese_text}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            result = response.choices[0].message.content.strip()
            
            # 去除 <think> 标签内容
            import re
            result = re.sub(r'<think>.*?</think>\s*', '', result, flags=re.DOTALL)
            
            return result.strip()
        except Exception as e:
            return f"翻译错误: {str(e)}"


if __name__ == "__main__":
    # 测试翻译功能
    translator = Translator()
    test_text = "你好，世界！今天天气真不错。"
    result = translator.translate(test_text)
    print(f"原文: {test_text}")
    print(f"译文: {result}")
