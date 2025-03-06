import os
from pathlib import Path

# 加载环境变量
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

class Config:
    # 文件存储路径
    BASE_PAPER_DIR = Path("storage/papers").absolute()  # 修改点：基础存储目录
    VECTOR_DB_PATH = Path("storage/vectors").absolute()
    
    # 大模型配置（硅基流动示例）
    SILICONFLOW_API_KEY = "sk-cgsiidhwchkefzjmqnjhpbnwieehrnrgbebstxkwqxfsvuie"
    SILICONFLOW_API_URL = "https://api.siliconflow.cn/v1"
    
    # 爬虫配置
    CRAWL_DELAY = 1  # 爬虫延迟时间（秒）
    DOWNLOAD_RETRIES = 3  # 下载重试次数
    RETRY_DELAY = 5  # 重试延迟时间（秒）

# 初始化存储目录
Config.BASE_PAPER_DIR.mkdir(parents=True, exist_ok=True)
Config.VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)