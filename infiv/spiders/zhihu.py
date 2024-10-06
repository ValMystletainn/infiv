import os
import random
import time
from typing import TYPE_CHECKING, List, Optional
from datetime import datetime

import bs4
import requests

from infiv.utils import html_to_info_item_markdown

if TYPE_CHECKING:
    from infiv.types import InfoItem

assert "ZHIHU_COOKIE" in os.environ, "This function needs ZHIHU_COOKIE to get the info, please login zhihu web and f12 -> console -> type `document.cookie` to get the login infomation"
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Sec-Ch-Ua-Platform': "Linux",
    'Sec-Ch-Ua-Mobile': "?0",
    'Cookie': os.environ["ZHIHU_COOKIE"],
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6,ak;q=0.5'
}

def answer_extract(content: bytes) -> "InfoItem":
    soup = bs4.BeautifulSoup(content, "html.parser")
    question_title = soup.select_one("h1.QuestionHeader-title").text.strip()
    answer_html = soup.select_one("div.RichContent").prettify()
    answer_md = html_to_info_item_markdown(answer_html)
    if len(answer_md) > 5000:  # TODO refactor as max_length
        answer_md = answer_md[:5000] + "..."
    
    return {
        "title": question_title,
        "content": answer_md,
        "pub_datetime": datetime.now(),  # refresh every time to avoid filtering
        "tags": [],
        "links": []
    }

def article_extract(content: bytes) -> "InfoItem":
    soup = bs4.BeautifulSoup(content, "html.parser")
    title = soup.select_one("h1.Post-Title").text.strip()
    content_html = soup.select_one("div.Post-RichTextContainer").prettify()
    content_md = html_to_info_item_markdown(content_html)
    if len(content_md) > 5000:
        content_md = content_md[:5000] + "..."
    
    return {
        "title": title,
        "content": content_md,
        "pub_datetime": datetime.now(),  # refresh every time to avoid filtering
        "tags": [],
        "links": []
    }


def get_page(url: str, single_page_timeout: float=5.) -> Optional["InfoItem"]:
    resp = requests.get(url, headers=headers, timeout=single_page_timeout)
    if resp.status_code != 200:
        raise RuntimeError("cannot fetch zhihu page please check your cookie")
    if url.startswith("https://zhuanlan.zhihu.com"):
        result = article_extract(resp.content)
        result["links"].append({"zhihu": url})
        return result
    elif url.startswith("https://www.zhihu.com/question"):
        result = answer_extract(resp.content)
        result["links"].append({"zhihu": url})
        return result
    return None

def parse_recommand_item(soup: bs4.Tag) -> "InfoItem":
    title_tag = soup.select_one('a[data-za-detail-view-element_name="Title"]')
    title = title_tag.text.strip()
    url = f"https:{title_tag.attrs['href']}"
    summary = soup.select_one("div.RichContent-inner").prettify()
    summary = html_to_info_item_markdown(summary)
    summary = summary.strip().rstrip("…\n \n\n\n 阅读全文\n \n \u200b") + '...'
    return {
        "title": title,
        "content": summary,
        "pub_datetime": datetime.now(),  # refresh every time to avoid filtering
        "tags": [],
        "links": [{"zhihu": url}]
    }

def get_info(url: str, single_page_timeout: float=5., max_items: int = 10) -> List["InfoItem"]:
    # # fail to do so, this is a js wait need playright
    # page_urls = []
    # while len(page_urls) < max_items:
    #     resp = requests.get(url, headers=headers, timeout=single_page_timeout)
    #     if resp.status_code != 200:
    #         raise RuntimeError("cannot fetch zhihu time line please check your cookie")
        
    #     ## extract url and title
    #     soup = bs4.BeautifulSoup(resp.content, "html.parser")
        
    #     recommand_items = soup.select('a[data-za-detail-view-element_name="Title"]')
    #     page_urls += [f"https:{item.attrs['href']}" for item in recommand_items]
    #     time.sleep(random.uniform(0.5, 1.5))
    
    # results = []
    # for page_url in page_urls:
    #     results.append(get_page(page_url)) 
    #     time.sleep(random.uniform(0.5, 1.5))

    all_items = []
    while len(all_items) < max_items:
        resp = requests.get(url, headers=headers, timeout=single_page_timeout)
        if resp.status_code != 200:
            raise RuntimeError("cannot fetch zhihu time line please check your cookie")
        soup = bs4.BeautifulSoup(resp.content, "html.parser")

        recommand_items = soup.select('div.ContentItem')
        all_items += recommand_items
    all_items = all_items[:max_items]
    
    results = [parse_recommand_item(item) for item in all_items]
    
    return results
    

if __name__ == '__main__':
    url = 'https://www.zhihu.com/'
    print(get_info(url))
    