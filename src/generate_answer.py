import os
from chromadb import PersistentClient
from chromadb.errors import InvalidCollectionException
from config.settings import Config
import requests
import chromadb

# Step 1: 查询处理并调用大模型 - 使用硅基流动API，并打印中文提示表示查询过程
def query_and_generate_answer(query, db_path, top_k=5):
    print("正在处理查询并生成答案...")  # 中文输出
    print(db_path)
    client = PersistentClient(path=db_path)
    collection = client.get_collection(name="pdf_collection")
    # 获取查询的嵌入
    payload = {
        "model": "BAAI/bge-m3",  # 更新模型名称
        "input": query,
        "encoding_format": "float"
    }
    
    response = requests.post(
        "https://api.siliconflow.com/v1/embeddings",
        headers={"Authorization": f"Bearer {Config.SILICONFLOW_API_KEY}", "Content-Type": "application/json"},
        json=payload
    )
    query_embedding = response.json().get('data')[0].get('embedding')

    # 使用ChromaDB进行最近邻搜索
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    
    relevant_texts = [doc for doc in results['documents'][0]]
    
    # 调用API获取回答
    url = "https://api.siliconflow.com/v1/chat/completions"
    data = {
        "model": "Pro/deepseek-ai/DeepSeek-R1",
        "messages": [
            {
                "role": "user",
                "content": "\n".join(relevant_texts) + "\n\nUser question: " + query,
            }
        ],
        "stream": False,
        "max_tokens": 1000,
        "temperature": 0.7
    }
    
    response = requests.post(url, headers={"Authorization": f"Bearer {Config.SILICONFLOW_API_KEY}", "Content-Type": "application/json"}, json=data)
    answer = response.json().get('choices')[0].get('message').get('content')
    print("查询完成，正在生成答案...")  # 中文输出
    return answer


