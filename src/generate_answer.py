import os
import json
from pathlib import Path
from chromadb import PersistentClient
import requests

# 假设这些是从配置文件导入的常量
from config.settings import Config

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

def query_and_generate_answer(query, db_path, conversation_id=None, top_k=Config.TOP_K):
    print(conversation_id) if conversation_id else None
    print("正在处理查询并生成答案...")
    client = PersistentClient(path=db_path)
    collection = client.get_collection(name="pdf_collection")  # 确保集合名称与实际一致

    # 构建并发送请求以获取查询嵌入
    payload = {
        "model": "BAAI/bge-m3",
        "input": query,
        "encoding_format": "float"
    }
    
    response = requests.post(
        f"{Config.BASE_URL}/embeddings",
        headers={"Authorization": f"Bearer {Config.API_KEY}", "Content-Type": "application/json"},
        json=payload
    )
    query_embedding = response.json().get('data')[0].get('embedding')

    # 查询数据库以获取相关文本
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    
    relevant_texts = [doc for doc in results['documents'][0]]
    
    # 加载或初始化对话历史
    conversation_history = load_conversation(conversation_id) if conversation_id is not None else []
    
    # 添加当前问题到消息列表中
    messages = conversation_history.copy()  # 复制对话历史以避免修改原始列表
    messages.append({"role": "user", "content": "\n".join(relevant_texts) + "\n\nUser question: " + query})
    
    # 调用API获取回答
    url = f"{Config.BASE_URL}/chat/completions"
    data = {
        "model": "Pro/deepseek-ai/DeepSeek-R1",
        "messages": messages,
        "stream": False,
        "max_tokens": 4096,
        "temperature": 0.7
    }
    
    response = requests.post(url, headers={"Authorization": f"Bearer {Config.API_KEY}", "Content-Type": "application/json"}, json=data)
    answer = response.json().get('choices')[0].get('message').get('content')
    
    # 更新对话历史
    messages.append({"role": "assistant", "content": answer})
    
    # 如果有conversation_id，则保存对话历史
    if conversation_id is not None:
        save_conversation(conversation_id, messages)
    
    print("查询完成，正在生成答案...")
    return answer