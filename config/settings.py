import os
from pathlib import Path

class Config:
    # 文件存储路径
    BASE_PAPER_DIR = Path("storage/papers").absolute()  # 修改点：基础存储目录
    
    # 大模型配置
    API_KEY = "sk-xxx"  # 替换成你的api-key
    BASE_URL = "https://api.siliconflow.cn/v1"  # 你使用的api的base-url，这里用的是硅基流动
    CHAT_MODEL = "Pro/deepseek-ai/DeepSeek-R1"  # 对话推理模型
    EMBEDDING_MODEL = "BAAI/bge-m3"  # 文本嵌入模型

    # 对话配置
    MAX_TOKEN = 2048  # 生成的最大token数，若生成被截断可以增大该值
    TEMPERATURE = 0.7  # 生成的稳定度，越低回答越准确，越高回答越发散

    # 检索配置
    TOP_K = 10  # 检索最相关的TopK条数据
    
    # 爬虫配置
    CRAWL_DELAY = 1  # 爬虫延迟时间（秒）
    DOWNLOAD_RETRIES = 3  # 下载重试次数
    RETRY_DELAY = 5  # 重试延迟时间（秒）

# 初始化存储目录
Config.BASE_PAPER_DIR.mkdir(parents=True, exist_ok=True)
