import subprocess

from flask import Flask, request, jsonify
from pathlib import Path

from main import infer_keywords_from_description
from src.crawlers import ArXivCrawler, ACLAnthologyCrawler
from src.update_vector_db import update_vector_db
from main import advise



app = Flask(__name__)


@app.route('/api/collect', methods=['POST'])
def collect():
    data = request.get_json()
    # 获取关键词列表或主题描述
    keywords = data.get('keywords')  # 预期为列表，例如 ["transformer", "llm"]
    description = data.get('description')  # 主题描述，用于自动推断关键词
    max_results = data.get('max', 50)
    source = data.get('source', 'arxiv')
    sort_by = data.get('sort', 'relevance')

    # 检查参数，必须提供 keywords 或 description 中的一个
    if not keywords and not description:
        return jsonify({"error": "未指定有效的关键词或描述"}), 400

    # 如果提供了 description 且未提供 keywords，则通过描述自动推断关键词
    if not keywords and description:
        try:
            keywords = infer_keywords_from_description(description)
        except Exception as e:
            return jsonify({"error": "关键词推断失败: " + str(e)}), 500

    # 根据数据源选择相应的爬虫
    try:
        if source == 'arxiv':
            crawler = ArXivCrawler()
        else:
            crawler = ACLAnthologyCrawler()
        crawler.collect_papers(keywords=keywords, max_results=max_results, sort_by=sort_by)
        return jsonify({"message": "论文收集成功", "keywords": keywords}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/update_db', methods=['POST'])
def update_db():
    data = request.get_json()
    keywords = data.get('keywords')

    # 如果提供了关键词，则只更新指定文件夹，否则更新所有文件夹
    if keywords:
        directory = Path("storage/papers") / keywords.replace(' ', '_')
    else:
        directory = Path("storage/papers")

    try:
        pdflist=update_vector_db(directory)
        #将pdflist的set转为JSON
        pdflist = list(pdflist)

        return jsonify({"message": "数据库更新成功", "pdflist": pdflist}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500




if __name__ == '__main__':
    # 仅在开发时使用 debug 模式，生产环境推荐使用gunicorn或其他WSGI服务器
    app.run(host='0.0.0.0', port=5000, debug=True)
