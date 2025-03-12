import requests
from config.settings import Config

class APIClient:
    """封装 API 交互，简化请求逻辑"""

    def __init__(self, base_url=Config.BASE_URL, api_key=Config.API_KEY, chat_model = Config.CHAT_MODEL, embedding_model = Config.EMBEDDING_MODEL, max_token = Config.MAX_TOKEN, temperature = Config.TEMPERATURE):
        self.base_url = base_url
        self.api_key = api_key
        self.chat_model = chat_model
        self.embedding_model = embedding_model
        self.max_token = max_token
        self.temperature = temperature
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

    def get_embeddings(self, text):
        """获取文本的嵌入向量"""
        payload = {
            "model": self.embedding_model,
            "input": text,
            "encoding_format": "float"
        }
        response = self.post("embeddings", payload)
        if response:
            return response.get('data')[0].get('embedding')
        return None

    def chat_completion(self, messages):
        """获取聊天模型的回答"""
        payload = {
            "model": self.chat_model,
            "messages": messages,
            "stream": False,
            "max_tokens": self.max_token,
            "temperature": self.temperature
        }
        response = self.post("chat/completions", payload)
        if response:
            return response.get('choices')[0].get('message').get('content')
        return None
