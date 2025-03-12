import os
from pathlib import Path

class Config:
    # 文件存储路径
    BASE_PAPER_DIR = Path("storage/papers").absolute()  # 修改点：基础存储目录
    
    # 大模型配置
    API_KEY = "sk-fyevldlvklxrhtzdnyqrbxewauldwueywbwwjxltlhqofurk"  # 替换成你的api-key
    BASE_URL = "https://api.siliconflow.cn/v1"  # 你使用的api的base-url，这里用的是硅基流动

    # 检索配置
    TOP_K = 10  # 检索最相关的TopK条数据
    
    # 爬虫配置
    CRAWL_DELAY = 1  # 爬虫延迟时间（秒）
    DOWNLOAD_RETRIES = 3  # 下载重试次数
    RETRY_DELAY = 5  # 重试延迟时间（秒）

# 初始化存储目录
Config.BASE_PAPER_DIR.mkdir(parents=True, exist_ok=True)
