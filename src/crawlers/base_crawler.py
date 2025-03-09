from abc import ABC, abstractmethod
import requests
import logging
from pathlib import Path
import time

from config.settings import Config

logger = logging.getLogger(__name__)

class BaseCrawler(ABC):
    """所有爬虫的基类"""

    def __init__(self, pdf_base_url):
        self.pdf_base_url = pdf_base_url
        self.headers = {'User-Agent': 'ResearchHelper'}

    @abstractmethod
    def search_papers(self, keyword, max_results=10, sort_by="relevance"):
        """搜索论文，返回结果列表"""
        pass


    def download_paper(self, paper_id, save_dir, max_retries=3, delay=5):
        """下载论文"""
        url = f"{self.pdf_base_url}{paper_id}.pdf"
        Path(save_dir).mkdir(parents=True, exist_ok=True)
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=self.headers)
                if response.status_code == 200:
                    file_path = Path(save_dir) / f"{paper_id}.pdf"
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    return {'success': True, 'path': str(file_path)}
                else:
                    time.sleep(delay)
            except Exception as e:
                logger.error(f"下载失败: {str(e)}")
                time.sleep(delay)
        return {'success': False}

    def collect_papers(self, keywords: list, max_results: int = 100, sort_by: str="relevance") -> None:
        for keyword in keywords:
            logger.info(f"正在收集关键词 '{keyword}' 的论文...")
            save_dir = Config.BASE_PAPER_DIR / keyword.replace(' ', '_')
            papers = self.search_papers(keyword=keyword, max_results=max_results, sort_by=sort_by)
            for paper in papers:
                try:
                    result = self.download_paper(paper_id=paper['id'], save_dir=save_dir, max_retries=Config.DOWNLOAD_RETRIES, delay=Config.RETRY_DELAY)
                    if result['success']:
                        pdf_path = result['path']
                        logger.info(f"成功下载论文: {paper['title']}")
                except Exception as e:
                    logger.error(f"下载论文 {paper['title']} 失败: {str(e)}")
                    continue
