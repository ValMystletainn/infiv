import os
import random
import time
from datetime import datetime
from typing import TYPE_CHECKING, List

import feedparser
import requests

from infiv.utils import strcut_time_to_datetime

if TYPE_CHECKING:
    from infiv.types import InfoItem, RSSFeedDict

expired_datetime = os.environ.get("EXPIRED_DAYTIME", None)
if expired_datetime is not None:
    try:
        expired_datetime = datetime.strptime(expired_datetime, r"%Y/%m/%d")
    except ValueError:
        expired_datetime = datetime.strptime(expired_datetime, r"%Y/%m/%d %H:%M")

def _convert_entry_to_info_item(entry: List["RSSFeedDict"]) -> "InfoItem":
    title = entry["title"]
    abstract = entry["summary"]
    link = entry["link"]
    arxiv_number = link.split("/")[-1]
    abs_link = f"https://arxiv.org/abs/{arxiv_number}"
    html_link = f"https://arxiv.org/html/{arxiv_number}"
    pdf_link = f"https://arxiv.org/pdf/{arxiv_number}"
    kimi_link = f"https://papers.cool/arxiv/{arxiv_number}"
    result = {
        "title": title,
        "content": abstract,
        "links": [
            {"arxiv": abs_link},
            {"html": html_link},
            {"pdf": pdf_link},
            {"kimi": kimi_link},
        ],
        "pub_datetime": strcut_time_to_datetime(entry["published_parsed"]),
        "tags": []
    }  # type: InfoItem

    return result


def get_info(url: str, timeout: float=60.0) -> List["InfoItem"]:
    if "/" in url:
        # formatter like
        # https://arxiv.org/list/cs.CV/recent?skip=87&show=50
        cat = url.split("/")[4]
    else:
        cat = url
    num_items_per_query = 1000
    responses = []
    now_datetime = datetime.now()

    ## YYYYMMDDTTTT
    expired_datetime_str = expired_datetime.strftime(r"%Y%m%d%H%M")
    now_datetime_str = now_datetime.strftime(r"%Y%m%d%H%M")

    for i in range(0, 1000):  # has a upper limit
        start = i * num_items_per_query
        url = f'http://export.arxiv.org/api/query?search_query=cat:{cat}+AND+submittedDate:[{expired_datetime_str}+TO+{now_datetime_str}]&sortBy=lastUpdatedDate&sortOrder=descending&start={start}&max_results={num_items_per_query}'

        data = requests.get(url, timeout=timeout).content.decode('utf-8')
        data = feedparser.parse(data)
        if len(data['entries']) == 0:
            break

        responses.extend(data['entries'])

        time.sleep(random.random() * 10 + 1)
    
    info_items = [_convert_entry_to_info_item(entry) for entry in responses]
    return info_items


if __name__ == '__main__':
    url = "cs.CV"  # also ok
    # url = "https://arxiv.org/list/cs.CV/recent?skip=87&show=50"
    info_list = get_info(url)
    print(info_list)
    print(f"{len(info_list)=}")
    names = [info["title"] for info in info_list]
    print(f"{len(names)=}")
    print(f"{len(set(names))=}")
