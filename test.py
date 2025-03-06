import os
import fitz  # PyMuPDF
import requests
from chromadb.config import Settings
from chromadb import Client
from chromadb.errors import InvalidCollectionException
import chromadb

# Step 1: 提取PDF内容，并打印中文提示表示开始处理
def extract_text_from_pdf(pdf_path):
    print("正在从PDF文件中提取文本：", pdf_path)  # 中文输出
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

# Step 2: 文本分割（现在支持重叠），并打印中文提示表示开始分割
def split_text_into_chunks(text, chunk_size=300, overlap=50):
    print("正在将文本分割成块...")  # 中文输出
    words = text.split()
    chunks = []
    
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = ' '.join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
        
    return chunks

# Step 4 & 5: 查询处理并调用大模型 - 同样使用硅基流动API，并打印中文提示表示查询过程
def query_and_generate_answer(query, collection, api_key, top_k=5):
    print("正在处理查询并生成答案...")  # 中文输出
    payload = {
        "model": "BAAI/bge-m3",  # 更新模型名称
        "input": query,
        "encoding_format": "float"
    }

    response = requests.post(
        "https://api.siliconflow.com/v1/embeddings",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload
    )
    query_embedding = response.json().get('data')[0].get('embedding')

    # 使用ChromaDB进行最近邻搜索
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    # print(results)
    relevant_texts = [doc for doc in results['documents'][0]]
    # print(relevant_texts)
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
    response = requests.post(url, headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, json=data)
    answer = response.json().get('choices')[0].get('message').get('content')
    print("查询完成，正在生成答案...")  # 中文输出
    return answer

# Step 3: 创建或加载向量索引 - 使用硅基流动API和ChromaDB，并打印中文提示表示开始创建/加载索引
def create_or_load_index(directory, api_key, chunk_size=300, overlap=50):
    print("正在检查或创建向量索引...")  # 中文输出
    client = chromadb.PersistentClient(path="D:/Workspace/ResearchHelper/chroma_db")

    try:
        collection = client.get_collection(name="pdf_collection")
        print("已找到现有向量索引，正在加载...")
    except InvalidCollectionException:
        print("未找到现有向量索引，正在创建新索引...")
        collection = client.create_collection(name="pdf_collection")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        ids = []
        metadatas = []
        documents = []
        embeddings = []

        for filename in os.listdir(directory):
            if filename.endswith('.pdf'):
                pdf_path = os.path.join(directory, filename)
                text = extract_text_from_pdf(pdf_path)
                chunks = split_text_into_chunks(text, chunk_size, overlap)

                for chunk in chunks:
                    payload = {
                        "model": "BAAI/bge-m3",  # 更新模型名称
                        "input": chunk,
                        "encoding_format": "float"
                    }

                    response = requests.post(
                        "https://api.siliconflow.cn/v1/embeddings",
                        headers=headers,
                        json=payload
                    )
                    embedding = response.json().get('data')[0].get('embedding')

                    if embedding:
                        id_str = f"{filename}_{len(ids)}"
                        ids.append(id_str)
                        embeddings.append(embedding)
                        metadatas.append({"filename": filename})
                        documents.append(chunk)
                        
        # 将数据添加到ChromaDB集合
        collection.add(
            embeddings=embeddings,  
            metadatas=metadatas,
            ids=ids,
            documents=documents
        )

    return collection

# 主程序入口
if __name__ == "__main__":
    directory = 'D:\\Workspace\\ResearchHelper\\storage\\papers\\large_language_models'  # Windows路径需使用双反斜杠
    api_key = "sk-cgsiidhwchkefzjmqnjhpbnwieehrnrgbebstxkwqxfsvuie"  # 替换为您的实际API密钥

    # 设置chunk的大小和overlap
    chunk_size = 300
    overlap = 50

    # 创建或加载索引
    collection = create_or_load_index(directory, api_key, chunk_size, overlap)

    # 用户输入问题
    user_query = "我是一名大模型行业从事者，我想进行大模型相关工作的研究，请你总结这几篇文章并告诉我哪些进一步工作是我可以作为学术创新点进行研究的。"

    # 获取答案
    answer = query_and_generate_answer(user_query, collection, api_key)
    print("最终答案如下：\n", answer)  # 中文输出