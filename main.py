import argparse

from src.crawlers.aclanthology_crawler import ACLAnthologyCrawler
from src.crawlers.arxiv_crawler import ArXivCrawler
from src.generate_answer import query_and_generate_answer
from src.update_vector_db import update_vector_db
from config.settings import Config
from pathlib import Path
import logging
import os
import requests
import json

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

def infer_keywords_from_description(description: str) -> list:
    url = f"{Config.BASE_URL}/chat/completions"
    prompt = f"""以下是对某个研究领域的描述：{description}\n，请你据此描述，提炼出若干个英文关键词，你的回答需要严格遵循以下格式，且不能输出任何其他内容！
关键词数量：X（X为你认为需要提炼的英文关键词数）
关键词内容：[keyword1, keyword2, ...]（将你提炼出的英文关键词代替为keyword1, keyword2...）"""
    data = {
        "model": "Pro/deepseek-ai/DeepSeek-R1",
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "stream": False,
        "max_tokens": 1024,  # 由于只需要关键词，这里可以设置较小的值
        "temperature": 0.7
    }

    try:
        response = requests.post(
            url, 
            headers={
                "Authorization": f"Bearer {Config.API_KEY}", 
                "Content-Type": "application/json"
            }, 
            json=data
        )
        response.raise_for_status()  # 如果响应状态码表示错误，则抛出HTTPError
        
        answer = response.json().get('choices')[0].get('message').get('content')
        # print(response.json)
        print("正在分析用户描述以提取关键词...")
        print(answer)
        try:
            # 假设回答格式为简单的关键词列表，例如 "keyword1, keyword2, keyword3"
            kws = answer.split('[')[1].split(']')[0].split(', ')
            keywords = [kw.strip() for kw in kws]
            return keywords
        except requests.exceptions.RequestException as e:
            logger.error(f"生成关键词出现错误: {e}")
    
    except requests.exceptions.RequestException as e:
        logger.error(f"请求过程中出现错误: {e}")
        return []

history_path = Path("storage/history_chat")

def load_conversation(conversation_id):
    conversation_file = history_path / f"{conversation_id}.json"
    if conversation_file.exists():
        with open(conversation_file, 'r') as file:
            return json.load(file)
    else:
        return None

def save_conversation(conversation_id, conversation_history):
    if not history_path.exists():
        history_path.mkdir(parents=True)
    conversation_file = history_path / f"{conversation_id}.json"
    with open(conversation_file, 'w') as file:
        json.dump(conversation_history, file)

def advise(directory: str, query: str = None, conversation_id: int = None):
    if not query and conversation_id is None:
        query = "这个领域有哪些最新的研究方向值得尝试？"
    
    db_path = os.path.join(directory, 'chroma_db')
    if not os.path.exists(db_path):
        logger.error("未找到数据库，请先运行update_db命令以生成数据库。")
        return
    
    # 如果提供了conversation_id，则加载对话历史
    if conversation_id is not None:
        conversation_history = load_conversation(conversation_id)
        if conversation_history is None:
            print(f"对话ID {conversation_id} 不存在，请检查输入后重试。")
            return
        else:
            print("对话历史：")
            for message in conversation_history:
                role = "用户" if message["role"] == "user" else "助手"
                print(f"{role}: {message['content']}")
        
        while True:
            query = input("请输入您的问题（输入'quit'退出）：")
            if query.lower() == 'quit':
                break
            
            answer = query_and_generate_answer(query=query, db_path=db_path, conversation_id=conversation_id)
            print(f"助手: {answer}")
            
            # 更新对话历史
            conversation_history.append({"role": "user", "content": query})
            conversation_history.append({"role": "assistant", "content": answer})
            
            # 每次对话后都保存对话历史
            save_conversation(conversation_id, conversation_history)
    else:
        if query is None:
            query = input("请输入您的问题（输入'quit'退出）：")
            if query.lower() == 'quit':
                return
        
        answer = query_and_generate_answer(query=query, db_path=db_path)
        print(f"助手: {answer}")
        
        # 将用户的查询和助手的回答添加到对话历史中
        conversation_history = [{"role": "user", "content": query}, {"role": "assistant", "content": answer}]
        
        # 如果是新对话，询问是否需要保存对话ID
        save_input = input("是否要保存此对话？(y/n): ")
        if save_input.lower() == 'y':
            conversation_files = list(history_path.glob('*.json'))
            new_id = len(conversation_files) + 1  # 新对话ID基于已有文件数加1
            save_conversation(new_id, conversation_history)  # 保存带有当前对话的新对话
            print(f"已创建新对话，ID为{new_id}。")

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