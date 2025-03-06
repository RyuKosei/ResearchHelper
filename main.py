import argparse
from src.arxiv_crawler import ArXivCrawler
from src.generate_answer import query_and_generate_answer
from src.update_vector_db import update_vector_db
from config.settings import Config
from pathlib import Path
import logging
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('research_helper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def collect_papers(keywords: list, max_results: int = 100) -> None:
    crawler = ArXivCrawler()
    for keyword in keywords:
        logger.info(f"正在收集关键词 '{keyword}' 的论文...")
        save_dir = Config.BASE_PAPER_DIR / keyword.replace(' ', '_')
        papers = crawler.search_papers(keyword=keyword, max_results=max_results)
        for paper in papers:
            try:
                result = crawler.download_paper(paper_id=paper['id'], save_dir=save_dir, max_retries=Config.DOWNLOAD_RETRIES, delay=Config.RETRY_DELAY)
                if result['success']:
                    pdf_path = result['path']
                    logger.info(f"成功下载论文: {paper['title']}")
            except Exception as e:
                logger.error(f"下载论文 {paper['title']} 失败: {str(e)}")
                continue

def advise(directory: str, query: str = None):
    # 如果没有提供query，则使用默认值
    if not query:
        query = "这个领域有哪些最新的研究方向值得尝试？"
    
    db_path = os.path.join(directory, 'chroma_db')
    if not os.path.exists(db_path):
        logger.error("未找到数据库，请先运行update_db命令以生成数据库。")
        return
    
    answer = query_and_generate_answer(query=query, db_path=db_path)
    
    print(f"{answer}")

def main():
    parser = argparse.ArgumentParser(description="科研研究方向分析工具")
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Collect command
    collect_parser = subparsers.add_parser('collect', help='收集论文')
    collect_parser.add_argument('-k', '--keywords', nargs='+', required=True, help='搜索关键词列表（例如：transformer llm）')
    collect_parser.add_argument('-m', '--max', type=int, default=50, help='每个关键词最大获取论文数（默认：50）')

    # Update DB command
    update_db_parser = subparsers.add_parser('update_db', help='更新向量数据库')
    update_db_parser.add_argument('-k', '--keywords', type=str, required=False, help='指定要更新的文件夹名称（例如：large_language_model），如果不指定，则更新所有文件夹')

    # Advise command
    advise_parser = subparsers.add_parser('advise', help='根据数据库中的内容提供建议')
    advise_parser.add_argument('-k', '--keywords', type=str, required=True, help='提供关键词以确定要使用的数据库')
    advise_parser.add_argument('-q', '--query', type=str, default=None, help='用户的查询（可选）')

    args = parser.parse_args()

    if args.command == 'collect':
        collect_papers(args.keywords, args.max)
    elif args.command == 'update_db':
        folder_name = args.keywords if hasattr(args, 'keywords') else None
        directory = Path(Config.BASE_PAPER_DIR) / (folder_name.replace(' ', '_') if folder_name else '')
        update_vector_db(directory)
        pass
    elif args.command == 'advise':
        folder_name = args.keywords if hasattr(args, 'keywords') else None
        directory = Path(Config.BASE_PAPER_DIR) / (folder_name.replace(' ', '_') if folder_name else '')
        advise(directory=directory, query=args.query)

if __name__ == "__main__":
    main()