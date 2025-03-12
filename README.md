# 科研方向助手（Research Helper）

## 项目结构
```
ResearchHelper/
├── src/                           # 代码目录
│   ├── arxiv_crawler.py           # arXiv爬虫实现
│   ├── aclanthology_crawler.py    # ACL anthology爬虫实现
│   ├── update_vector_db.py        # 更新向量数据库
│   └── generate_answer.py         # 生成科研方向建议
├── config/                        # 配置管理
│   └── settings.py       
├── storage/                       # 论文存储 
│   ├── papers/                    # PDF存储目录（自动创建）
│   └── history_chat/              # 对话历史记录（自动创建）
├── requirements.txt               # 依赖库
└── main.py                        # 主程序入口
```

## 待完成内容
```
自动更新功能

向量库重置功能

其余api支持

多模态支持（目前只支持pdf中的文字内容）

前端设计

提高下载pdf后命名可读性

优化开启对话的逻辑
```


## 使用示例

```bash
# macOS用户需要额外下载插件tools，Windows用户可以跳过这一步骤
pip install tools==0.1.9

# 安装依赖
pip install -r requirements.txt

# 在settings.py中设置你的base-url和api-key
API_KEY = "sk-xxx"  # 替换成你的api-key
API_URL = "https://api.siliconflow.cn/v1"  # 你使用的api的base-url，这里用的是硅基流动

# 抓取领域论文（以大语言模型为例），可以指定具体关键词，或者用自然语言描述指定领域方向以自动分析关键词，若不指定--max作为抓取的论文数量则默认为50
python main.py collect --keywords "large language models" --max 5
python main.py collect --description "大模型相关领域的方向" --max 3

# 更新数据库，若不指定--keywords则更新全部数据库
python main.py update_db --keywords "large language models" 

# 提出科研建议，若指定--query则发起新的对话，并产生一个新的id供调出历史记录；若指定--id则展示指定id对应的对话历史记录，并支持继续对话
python main.py advise --keywords "large language models" --query "我手头的算力资源并不充裕，从科研的角度来讲，我可以在哪些大模型的方向进行尝试呢？"
python main.py advise --keywords "large language models" --id 1
```

## 指令和参数
完整的指令说明请参考 [Research Helper 指令文档](https://gist.github.com/BoningZ/650007b56cffc21c79bbbf84a4ea8f0a)。
