import os
import random
import time
from datetime import datetime
from typing import TYPE_CHECKING, List

import bs4
import requests

from infiv.utils import html_to_info_item_markdown

if TYPE_CHECKING:
    from infiv.types import InfoItem


assert "BILIBILI_COOKIE" in os.environ, "This function needs BILIBILI_COOKIE to get the info, please login BILIBILI web and f12 -> console -> type `document.cookie` to get the login infomation"
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Sec-Ch-Ua-Platform': "Linux",
    'Sec-Ch-Ua-Mobile': "?0",
    'Cookie': os.environ["BILIBILI_COOKIE"],
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6,ak;q=0.5'
}

def get_page(url: str, single_page_timeout: float=10.) -> "InfoItem":
    resp = requests.get(url, headers=headers, timeout=single_page_timeout)
    if resp.status_code != 200:
        raise RuntimeError("cannot fetch bilibili page, please check your cookie")
    soup = bs4.BeautifulSoup(resp.content, "html.parser")
    
    title = soup.select_one("h1.video-title").text.strip()
    author = soup.select_one('a[class~="up-name"]').text.strip()
    pub_datetime = soup.select_one('div.pubdate-ip-text').text.strip()
    desc = soup.select_one('span.desc-info-text')
    desc = html_to_info_item_markdown(desc.prettify()) if desc is not None else ""

    summary = f"{author} post at {pub_datetime}\n\n {desc}"

    return {
        "title": title,
        "content": summary,
        "pub_datetime": datetime.now(),  # refresh every time to avoid filtering
        "tags": [],
        "links": [{"bilibili": url}]
    }
    

def get_info(url: str, single_page_timeout: float=10., max_items: int = 10) -> List["InfoItem"]:
    all_recommands = []  # type: List[bs4.Tag]
    while len(all_recommands) < max_items:
        resp = requests.get(url, headers=headers, timeout=single_page_timeout)
        if resp.status_code != 200:
            raise RuntimeError("cannot fetch bilibili page, please check your cookie")
        soup = bs4.BeautifulSoup(resp.content, "html.parser")
        recommand_items = soup.select('h3.bili-video-card__info--tit')
        ## filter out video skip adv
        video_urls = [item.select_one("a").attrs['href'] for item in recommand_items]
        recommand_items = [
            item for item, video_url in zip(recommand_items, video_urls)
            if video_url.startswith("https://www.bilibili.com/video/")
        ]
        all_recommands += recommand_items
        time.sleep(random.uniform(0.5, 1.5))
    all_recommands = all_recommands[:max_items]

    video_urls = [item.select_one("a").attrs['href'] for item in all_recommands]
    
    results = []
    for video_url in video_urls:
        results.append(get_page(video_url)) 
        time.sleep(random.uniform(0.5, 1.5))
    return results

if __name__ == '__main__':
    print(get_info("https://www.bilibili.com/"))        

