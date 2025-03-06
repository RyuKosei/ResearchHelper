# 科研方向助手（Research Helper）

## 项目结构
```
ResearchHelper/
├── src/                    # 代码目录
│   ├── arxiv_crawler.py    # arXiv爬虫实现
│   └── update_vector_db.py # 更新向量数据库
│   └── generate_answer.py  # 生成科研方向建议
├── config/                 # 配置管理
│   └── settings.py       
├── storage/                # 论文存储 
│   └── papers/             # PDF存储目录（自动创建）
├── requirements.txt        # 依赖库
└── main.py                 # 主程序入口
```

## 待完成内容
requirement.txt
泛化关键词描述（如：输入一句话，生成一些可能的关键词进行搜索）
更多数据库索引
自动更新功能
向量库重置功能
自定义对话建议
其余api支持
多模态支持（目前只支持pdf中的文字）

## 使用示例
```bash
# 安装依赖
pip install -r requirements.txt

# 抓取大模型相关论文
python main.py collect --keywords "large language models" --max 3

# 更新数据库
python main.py update_db --keywords "large language models" 

# 提出科研建议
python main.py advise --keywords "large language models" 