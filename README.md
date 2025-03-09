# 科研方向助手（Research Helper）

## 项目结构
```
ResearchHelper/
├── src/                           # 代码目录
│   ├── arxiv_crawler.py           # arXiv爬虫实现
│   ├── aclanthology_crawler.py    # ACL anthology爬虫实现
│   └── update_vector_db.py        # 更新向量数据库
│   └── generate_answer.py         # 生成科研方向建议
├── config/                        # 配置管理
│   └── settings.py       
├── storage/                       # 论文存储 
│   └── papers/                    # PDF存储目录（自动创建）
├── requirements.txt               # 依赖库
└── main.py                        # 主程序入口
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

## 指令和参数
### 1️⃣ `collect` (收集论文)
用于从 `arxiv` 或 `ACL Anthology` 爬取论文，并存入本地。

#### 💌 语法
```bash
python main.py collect --keywords <关键词1> <关键词2> ... --max <最大论文数> --source <数据源> --sort <排序方式>
```

#### 💌 可选参数
| 参数 | 说明 | 选项 | 默认值 |
|------|------|------|------|
| `-k, --keywords` | **搜索关键词列表**（多个用空格分隔） | 任意字符串 | 必填（与 `--description` 二选一） |
| `-d, --description` | **主题描述**（自动生成搜索关键词） | 任意字符串 | 必填（与 `--keywords` 二选一） |
| `-m, --max` | **每个关键词最大获取论文数** | 整数 | `50` |
| `-s, --source` | **数据源** | `arxiv` / `acl` | `arxiv` |
| `--sort` | **排序方式** | `relevance` / `latest` | `relevance` |

#### 💌 示例
```bash
# 1️⃣ 直接使用关键词搜索 10 篇 ACL 论文，按发布时间排序
python main.py collect --keywords "transformer" "LLM" --max 10 --source acl --sort latest

# 2️⃣ 使用自然语言描述，自动推断关键词并搜索 5 篇论文
python main.py collect --description "大模型优化方向" --max 5
```

---

### 2️⃣ `update_db` (更新向量数据库)
用于将本地爬取的论文数据更新到向量数据库。

#### 💌 语法
```bash
python main.py update_db --keywords <数据库名称>
```

#### 💌 可选参数
| 参数 | 说明 | 选项 | 默认值 |
|------|------|------|------|
| `-k, --keywords` | **指定要更新的数据库** | 数据库名称 | 不填则更新全部 |

#### 💌 示例
```bash
# 1️⃣ 只更新 "large language models" 相关数据库
python main.py update_db --keywords "large_language_model"

# 2️⃣ 更新所有数据库
python main.py update_db
```

---

### 3️⃣ `advise` (科研建议)
从数据库中获取科研方向建议，基于已有数据进行智能回答。

#### 💌 语法
```bash
python main.py advise --keywords <数据库名称> --query <问题>
```

#### 💌 可选参数
| 参数 | 说明 | 选项 | 默认值 |
|------|------|------|------|
| `-k, --keywords` | **指定数据库**（多个用 `,` 分隔） | 数据库名称 | 必填 |
| `-q, --query` | **用户查询**（科研问题） | 任意字符串 | 不填则提供研究方向建议 |

#### 💌 示例
```bash
# 1️⃣ 询问 "large language models" 相关的研究方向
python main.py advise --keywords "large_language_model"

# 2️⃣ 提出具体问题："算力有限，我应该研究什么方向？"
python main.py advise --keywords "large_language_model" --query "算力资源受限的情况下，我适合研究什么？"
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
python main.py collect --description "大模型相关领域的方向" --max 5

# 更新数据库，若不指定--keywords则更新全部数据库
python main.py update_db --keywords "large language models" 

# 提出科研建议，若不指定--query则默认询问研究方向
python main.py advise --keywords "large language models" --query "我手头的算力资源并不充裕，从科研的角度来讲，我可以在哪些大模型的方向进行尝试呢？"