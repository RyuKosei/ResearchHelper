import argparse
from src.crawlers.aclanthology_crawler import ACLAnthologyCrawler
from src.crawlers.arxiv_crawler import ArXivCrawler
from src.generate_answer import query_and_generate_answer, infer_keywords_from_description, advise
from src.update_vector_db import update_vector_db
from config.settings import Config
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('research_helper.log'),
        logging.StreamHandler()
    ]
)
logging.getLogger('chromadb.telemetry.product.posthog').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="科研研究方向分析工具")
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Collect command
    collect_parser = subparsers.add_parser('collect', help='收集论文')
    collect_group = collect_parser.add_mutually_exclusive_group(required=True)
    collect_group.add_argument('-k', '--keywords', nargs='+', help='搜索关键词列表（例如：transformer llm）')
    collect_group.add_argument('-d', '--description', type=str, help='主题描述，用于自动推断关键词')
    collect_parser.add_argument('-m', '--max', type=int, default=50, help='每个关键词最大获取论文数（默认：50）')
    collect_parser.add_argument('-s', '--source', choices=['arxiv', 'acl'], default='arxiv', help='数据源（arxiv 或 acl，默认 arxiv）')
    collect_parser.add_argument('--sort', choices=['relevance', 'latest'], default='relevance', help='排序方式（relevance: 相关度, latest: 最新）')

    # Update DB command
    update_db_parser = subparsers.add_parser('update_db', help='更新向量数据库')
    update_db_parser.add_argument('-k', '--keywords', type=str, required=False, help='指定要更新的文件夹名称（例如：large_language_model），如果不指定，则更新所有文件夹')

    # Advise command
    advise_parser = subparsers.add_parser('advise', help='根据数据库中的内容提供建议')
    advise_parser.add_argument('-k', '--keywords', type=str, required=True, help='提供关键词以确定要使用的数据库')
    group = advise_parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-q', '--query', type=str, help='用户的查询（当不使用--id时）')
    group.add_argument('--id', type=int, help='指定对话ID以加载历史记录')

    args = parser.parse_args()

    if args.command == 'collect':
        if args.keywords:
            keywords = args.keywords
        elif args.description:
            keywords = infer_keywords_from_description(args.description)
        else:
            raise ValueError("未指定有效的关键词或描述")
        if args.source == 'arxiv':
            crawler = ArXivCrawler()
        else:
            crawler = ACLAnthologyCrawler()
        crawler.collect_papers(keywords=keywords, max_results=args.max, sort_by=args.sort)
    elif args.command == 'update_db':
        folder_name = args.keywords if hasattr(args, 'keywords') else None
        directory = Path(Config.BASE_PAPER_DIR) / (folder_name.replace(' ', '_') if folder_name else '')
        update_vector_db(directory)
        pass
    elif args.command == 'advise':
        folder_name = args.keywords if hasattr(args, 'keywords') else None
        directory = Path(Config.BASE_PAPER_DIR) / (folder_name.replace(' ', '_') if folder_name else '')
        advise(directory=directory, query=args.query, conversation_id=args.id)

if __name__ == "__main__":
    main()