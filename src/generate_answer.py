import os
from chromadb import PersistentClient
from config.settings import Config
import requests

def query_and_generate_answer(query, db_path, top_k=Config.TOP_K):
    print("正在处理查询并生成答案...") 
    print(db_path)
    client = PersistentClient(path=db_path)
    collection = client.get_collection(name="pdf_collection")

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

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    
    relevant_texts = [doc for doc in results['documents'][0]]
    
    # 调用API获取回答
    url = f"{Config.BASE_URL}/chat/completions"
    data = {
        "model": "Pro/deepseek-ai/DeepSeek-R1",
        "messages": [
            {
                "role": "user",
                "content": "\n".join(relevant_texts) + "\n\nUser question: " + query,
            }
        ],
        "stream": False,
        "max_tokens": 4096,
        "temperature": 0.7
    }
    
    response = requests.post(url, headers={"Authorization": f"Bearer {Config.API_KEY}", "Content-Type": "application/json"}, json=data)
    answer = response.json().get('choices')[0].get('message').get('content')
    print("查询完成，正在生成答案...") 
    return answer


