import os
import pymupdf  
from chromadb import PersistentClient
from chromadb.errors import InvalidCollectionException
import requests
from config.settings import Config

def extract_text_from_pdf(pdf_path):
    print("正在从PDF文件中提取文本：", pdf_path)
    doc = pymupdf.open(pdf_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

def split_text_into_chunks(text, chunk_size=300, overlap=50):
    print("正在将文本分割成块...")
    words = text.split()
    chunks = []
    
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = ' '.join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
        
    return chunks

def update_vector_db(directory, chunk_size=300, overlap=50):
    db_path = os.path.join(directory, 'chroma_db')
    client = PersistentClient(path=db_path)

    try:
        collection = client.get_collection(name="pdf_collection")
        print("已找到现有向量索引，正在加载...")
    except InvalidCollectionException:
        collection = client.create_collection(name="pdf_collection")
        print("未找到现有向量索引，正在创建新索引...")
    existing_files = {metadata['filename'] for metadata in collection.get()['metadatas']}

    if existing_files != ():
        print("当前数据库中的文件列表：")
        print(existing_files)
    else:
        print("当前数据库中无已入库文件.")
    headers = {
        "Authorization": f"Bearer {Config.API_KEY}",
        "Content-Type": "application/json"
    }

    for filename in os.listdir(directory):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(directory, filename)
            # print(filename)
            if filename in existing_files:
                continue
            
            text = extract_text_from_pdf(pdf_path)
            chunks = split_text_into_chunks(text, chunk_size, overlap)

            ids = []
            metadatas = []
            documents = []
            embeddings = []

            for chunk in chunks:
                payload = {
                    "model": "BAAI/bge-m3",
                    "input": chunk,
                    "encoding_format": "float"
                }

                response = requests.post(
                    f"{Config.BASE_URL}/embeddings",
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
                    
            collection.add(
                embeddings=embeddings,  
                metadatas=metadatas,
                ids=ids,
                documents=documents
            )
    print("向量数据库更新完成.")