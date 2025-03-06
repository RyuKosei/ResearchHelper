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
```
泛化关键词描述（如：输入一句话，生成一些可能的关键词进行搜索）

更多数据库索引

自动更新功能

向量库重置功能

其余api支持

多模态支持（目前只支持pdf中的文字内容）
```
## 使用示例
```bash
# 安装依赖
pip install -r requirements.txt

# 在settings.py中设置你的base-url和api-key
API_KEY = "sk-xxx"  # 替换成你的api-key
API_URL = "https://api.siliconflow.cn/v1"  # 你使用的api的base-url，这里用的是硅基流动

# 抓取领域论文（以大语言模型为例）
python main.py collect --keywords "large language models" --max 5

# 更新数据库，若不指定--keywords则更新全部数据库
python main.py update_db --keywords "large language models" 

# 提出科研建议，若不指定--query则默认询问研究方向
python main.py advise --keywords "large language models" --query "我手头的算力资源并不充裕，从科研的角度来讲，我可以在哪些大模型的方向进行尝试呢？"