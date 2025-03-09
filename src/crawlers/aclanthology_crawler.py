import time
from bs4 import BeautifulSoup
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager

from .base_crawler import BaseCrawler

logger = logging.getLogger(__name__)

class ACLAnthologyCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("https://aclanthology.org/")
        self.base_url = "https://aclanthology.org/"
        self.search_url = "https://aclanthology.org/search/?q="
        self.headers = {'User-Agent': 'ResearchHelper'}

        # 设置 Chrome 无头模式
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def search_papers(self, keyword, max_results=10, sort_by="relevance"):
        search_url = f"{self.search_url}{keyword.replace(' ', '+')}"
        self.driver.get(search_url)
        time.sleep(3)  # 等待页面加载

        if sort_by == "latest":
            try:
                sort_dropdown = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "gsc-selected-option-container"))
                )
                sort_dropdown.click()  # 模拟点击打开排序选项
                time.sleep(1)  # 等待下拉菜单展开

                year_sort_option = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@class='gsc-option' and text()='Year of Publication']"))
                )

                year_sort_option.click()
                time.sleep(3)  # 等待页面刷新

            except Exception as e:
                print(f"排序时出错: {str(e)}")

        entries = []
        seen_urls = set()
        count = 0
        current_page_number = 1  # 手动记录当前页码

        while count < max_results:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            results = soup.find_all("a", href=True)

            for result in results:
                href = result["href"].strip()
                if href.startswith(self.base_url) and len(href) > len(self.base_url):  # 确保是论文链接
                    paper_url = href.rstrip('/')

                    if paper_url in seen_urls:
                        continue
                    seen_urls.add(paper_url)

                    # 访问论文详情页获取详细信息
                    paper_data = self.get_paper_details(paper_url)
                    if paper_data:
                        entries.append(paper_data)
                        count += 1
                    if count >= max_results:
                        return entries

            # 处理翻页
            next_pages = self.driver.find_elements(By.CSS_SELECTOR, ".gsc-cursor-page")
            next_page = None
            for page in next_pages:
                if page.text.isdigit() and int(page.text) == current_page_number + 1:  # 选择下一页
                    next_page = page
                    break

            if next_page:
                current_page_number += 1  # 更新当前页码
                next_page.click()
                time.sleep(3)  # 等待新页面加载
            else:
                break  # 没有更多的页面

        return entries

    def get_paper_details(self, paper_url):
        try:
            self.driver.get(paper_url)
            time.sleep(2)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # 提取论文标题
            title_tag = soup.find("h2", id="title")
            title = title_tag.text.strip() if title_tag else "Unknown"

            # 提取论文PDF链接
            pdf_link_tag = title_tag.find("a", href=True) if title_tag else None
            pdf_url = pdf_link_tag["href"] if pdf_link_tag else "N/A"

            # 提取摘要
            abstract_tag = soup.find("div", class_="acl-abstract")
            summary = abstract_tag.find("span").text.strip() if abstract_tag else "N/A"

            # 提取作者
            authors = []
            author_tags = soup.select("p.lead a")
            for author in author_tags:
                authors.append(author.text.strip())

            # 提取发布时间
            published_tag = soup.find("dd", text=True)
            published = published_tag.text.strip() if published_tag else "Unknown"

            # 提取论文ID
            paper_id = paper_url.split('/')[-1]

            return {
                'title': title,
                'summary': summary,
                'pdf_url': pdf_url,
                'published': published,
                'authors': authors,
                'id': paper_id
            }
        except Exception as e:
            logger.error(f"抓取论文详情时出错: {str(e)}")
            return None

