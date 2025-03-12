import os
import json
from pathlib import Path
from chromadb import PersistentClient
import requests

# 假设这些是从配置文件导入的常量
from config.settings import Config
from src.api_client import APIClient

history_path = Path("storage/history_chat")

def load_conversation(conversation_id):
    conversation_file = history_path / f"{conversation_id}.json"
    if conversation_file.exists():
        with open(conversation_file, 'r') as file:
            return json.load(file)
    else:
        return []

def save_conversation(conversation_id, conversation_history):
    if not history_path.exists():
        history_path.mkdir(parents=True)
    conversation_file = history_path / f"{conversation_id}.json"
    with open(conversation_file, 'w') as file:
        json.dump(conversation_history, file)

def infer_keywords_from_description(description: str) -> list:
    api_client = APIClient()

    prompt = (
        f"以下是对某个研究领域的描述：{description}\n"
        f"请据此描述，提炼出若干个英文关键词，必须严格遵循以下格式，且不能输出任何其他内容：\n"
        f"关键词数量：X（X为你认为需要提炼的关键词数）\n"
        f"关键词内容：[keyword1, keyword2, ...]"
    )

    messages = [{"role": "user", "content": prompt}]
    try:
        response = api_client.chat_completion(messages,max_tokens=1024)
        print("正在分析用户描述以提取关键词...")
        print(response)
        try:
            kws = response.split('[')[1].split(']')[0].split(', ')
            return [kw.strip() for kw in kws]
        except Exception as e:
            print(f"生成关键词出现错误: {e}")
    except requests.exceptions.RequestException as e:
        print(f"请求过程中出现错误")
    return []


def advise(directory: str, query: str = None, conversation_id: int = None):
    """提供建议（基于数据库查询）"""
    if not query and conversation_id is None:
        query = "这个领域有哪些最新的研究方向值得尝试？"

    db_path = os.path.join(directory, 'chroma_db')
    if not os.path.exists(db_path):
        print("未找到数据库，请先运行 update_db 命令以生成数据库。")
        return

    # 加载对话历史
    if conversation_id is not None:
        conversation_history = load_conversation(conversation_id)
        if conversation_history is None:
            print(f"对话ID {conversation_id} 不存在，请检查输入后重试。")
            return
        else:
            print("对话历史：")
            for message in conversation_history:
                role = "用户" if message["role"] == "user" else "助手"
                print(f"====={role}=====\n{message['content']}")

        while True:
            query = input("请输入您的问题（输入 'q' 退出）：")
            if query.lower() == 'q':
                break

            answer = query_and_generate_answer(query=query, db_path=db_path, conversation_id=conversation_id)
            print(f"=====助手=====\n{answer}")

            # 更新并保存对话历史
            conversation_history.append({"role": "user", "content": query})
            conversation_history.append({"role": "assistant", "content": answer})
            save_conversation(conversation_id, conversation_history)
    else:
        if query is None:
            query = input("请输入您的问题（输入 'q' 退出）：")
            if query.lower() == 'q':
                return

        answer = query_and_generate_answer(query=query, db_path=db_path)
        print(f"=====助手=====\n{answer}")

        # 记录新对话
        conversation_history = [{"role": "user", "content": query}, {"role": "assistant", "content": answer}]

        # 询问是否保存对话
        save_input = input("是否要保存此对话？(y/n): ")
        if save_input.lower() == 'y':
            conversation_files = list(history_path.glob('*.json'))
            new_id = len(conversation_files) + 1
            save_conversation(new_id, conversation_history)
            print(f"已创建新对话，ID 为 {new_id}。")



def query_and_generate_answer(query, db_path, conversation_id=None, top_k=Config.TOP_K):
    # print(conversation_id) if conversation_id else None
    print("正在处理查询并生成答案...")
    client = PersistentClient(path=db_path)
    collection = client.get_collection(name="pdf_collection")  # 确保集合名称与实际一致

    api_client = APIClient()  # 初始化 API 客户端

    # 获取查询文本的嵌入向量
    query_embedding = api_client.get_embeddings(query)

    # 查询数据库获取相关文本
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    
    relevant_texts = [doc for doc in results['documents'][0]]
    
    # 加载或初始化对话历史
    conversation_history = load_conversation(conversation_id) if conversation_id is not None else []
    
    # 添加当前问题到消息列表中
    messages = conversation_history.copy()  # 复制对话历史以避免修改原始列表
    messages.append({"role": "user", "content": "\n".join(relevant_texts) + "\n\nUser question: " + query})
    
    # 调用API获取回答
    answer = api_client.chat_completion(messages)
    
    # 更新对话历史
    messages.append({"role": "assistant", "content": answer})
    
    # 如果有conversation_id，则保存对话历史
    if conversation_id is not None:
        save_conversation(conversation_id, messages)
    
    # print("查询完成，正在生成答案...")
    return answer