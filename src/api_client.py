import requests
from config.settings import Config

class APIClient:
    """封装 API 交互，简化请求逻辑"""

    def __init__(self, base_url=Config.BASE_URL, api_key=Config.API_KEY):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def post(self, endpoint, payload):
        """发送 POST 请求"""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()  # 发生 HTTP 错误时抛出异常
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求 {endpoint} 失败: {e}")
            return None

    def get_embeddings(self, text, model="BAAI/bge-m3"):
        """获取文本的嵌入向量"""
        payload = {
            "model": model,
            "input": text,
            "encoding_format": "float"
        }
        response = self.post("embeddings", payload)
        if response:
            return response.get('data')[0].get('embedding')
        return None

    def chat_completion(self, messages, model="Pro/deepseek-ai/DeepSeek-R1", max_tokens=4096, temperature=0.7):
        """获取聊天模型的回答"""
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        response = self.post("chat/completions", payload)
        if response:
            return response.get('choices')[0].get('message').get('content')
        return None
