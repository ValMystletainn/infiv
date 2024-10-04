# from markdownify import markdownify as md

# def custom_markdownify(html):
#     # 将 HTML 转换为 Markdown
#     markdown = md(html, heading_style="ATX")
    
#     # 处理标题，将标题转为加粗的独立一行文字
#     lines = markdown.splitlines()
#     for i, line in enumerate(lines):
#         if line.startswith('#'):  # 检查是否是标题
#             # 去掉标题的 '#' 和空格，并加粗
#             title_text = line.lstrip('#').strip()
#             lines[i] = f"**{title_text}**"  # 加粗标题
    
#     return "\n".join(lines)

# # 示例 HTML
# html_input = """
# <h1>This is a Title</h1>
# <p>This is a paragraph.</p>
# <h2>Another Title</h2>
# <p>Another paragraph.</p>
# """

# # 转换并打印结果
# markdown_output = custom_markdownify(html_input)
# print(markdown_output)

## test embedder
from infiv.spiders.rsshub.default import get_info
from infiv.type import InfoItem
import random
import google.generativeai as genai
import numpy as np

items = []
urls = [
    "http://localhost:1200/papers/arxiv/cs.AI",
    "http://localhost:1200/nature/research"
]

for url in urls:
    new_items = get_info(url)
    items.extend(new_items)



items = random.sample(items[:50], k=10) + random.sample(items[-20:], k=10)

## 试试 summzarize

temp_texts = []
for item in items:
    item: InfoItem
    temp_texts.append(f"##{item['title']}\n\n{item['content']}")

total_item = "\n\n".join(temp_texts)

prompt = f"""
You are a summarizer.
You are given a long markdown text, for today's news, each new is a markdown block start with a level2 head.
please summarize it.

today's news are given

{total_item}
"""

genai.configure(transport="rest")

# model = genai.GenerativeModel('gemini-1.5-flash')
# response = model.generate_content(prompt)
# print(response.text)

a = 0

## 得到 embedding

embeddings = []

items.append({"title": "medical imaging", "content": ""})

for item in items:
    item: InfoItem
    embedded_text = f"##{item['title']}\n\n{item['content']}"
    if len(embedded_text) > 5000:
        embedded_text = f"{embedded_text[:5000]}..."
    embedded_text = embedded_text[:5000]
    embedding = genai.embed_content(
        model="models/text-embedding-004",
        content=embedded_text,
        task_type="clustering"
    )["embedding"]
    embeddings.append(embedding)

embeddings = np.array(embeddings)

sim = np.dot(embeddings, embeddings.T)


a = 1
