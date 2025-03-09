import requests
import time
from pathlib import Path
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class ArXivCrawler:
    def __init__(self):
        self.base_url = "http://export.arxiv.org/api/query?"
        self.pdf_base_url = "http://arxiv.org/pdf/"
        self.headers = {'User-Agent': 'ResearchHelper'}

    def search_papers(self, keyword, max_results=10):
        query = f"search_query=all:{keyword}&start=0&max_results={max_results}"
        response = requests.get(self.base_url + query, headers=self.headers)
        return self.parse_results(response.text)

    def parse_results(self, xml_data):
        soup = BeautifulSoup(xml_data, 'lxml-xml')
        entries = []
        for entry in soup.find_all('entry'):
            paper = {
                'title': entry.title.text.strip(),
                'summary': entry.summary.text.strip(),
                'pdf_url': self.pdf_base_url + entry.id.text.split('/')[-1],
                'published': entry.published.text,
                'id': entry.id.text.split('/')[-1]
            }
            entries.append(paper)
        return entries

    def download_paper(self, paper_id, save_dir, max_retries=3, delay=5):
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