import requests
from bs4 import BeautifulSoup
import logging

from .base_crawler import BaseCrawler

logger = logging.getLogger(__name__)

class ArXivCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("http://arxiv.org/pdf/")
        self.base_url = "http://export.arxiv.org/api/query?"
        self.pdf_base_url = "http://arxiv.org/pdf/"
        self.headers = {'User-Agent': 'ResearchHelper'}

    def search_papers(self, keyword, max_results=10, sort_by="relevance"):
        sort_order = "relevance" if sort_by == "relevance" else "lastUpdatedDate"
        query = f"search_query=all:{keyword}&start=0&max_results={max_results}&sortBy={sort_order}&sortOrder=descending"
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
