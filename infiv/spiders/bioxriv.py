import random
import os
import re
import time
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

import requests
from bs4 import BeautifulSoup

from infiv.utils import html_to_info_item_markdown

if TYPE_CHECKING:
    from infiv.types import InfoItem


expired_datetime = os.environ.get("EXPIRED_DAYTIME", None)
if expired_datetime is not None:
    try:
        expired_datetime = datetime.strptime(expired_datetime, r"%Y/%m/%d")
    except ValueError:
        expired_datetime = datetime.strptime(expired_datetime, r"%Y/%m/%d %H:%M")


def extract_article_info(url: str, single_resq_timout: float = 60.) -> Optional["InfoItem"]:
    resp = requests.get(url, timeout=single_resq_timout)
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to fetch  content; {resp.status_code}, {resp.content=}")
    soup = BeautifulSoup(resp.content, "html.parser")
    abstract = soup.select_one("#abstract-1").prettify()
    abstract = html_to_info_item_markdown(abstract).strip()

    post_at_str = soup.select_one("#block-system-main > div > div > div > div > div.sidebar-right-wrapper.grid-10.omega > div > div > div.panel-pane.pane-custom.pane-1 > div").text

    pattern = r'(?i)(january|february|march|april|may|june|july|august|september|october|november|december) (\d{1,2}), (\d{4})'
    match = re.search(pattern, post_at_str)
    if match:
        month_name, day, year = match.groups()
        month = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }[month_name.lower()]
        pub_datetime = datetime(int(year), month, int(day), 23, 59, 59)
    else:
        pub_datetime = datetime.now()
    
    if expired_datetime is None or pub_datetime > expired_datetime:
        result = {
            "title": "",
            "content": abstract,
            "pub_datetime": pub_datetime,
            "links": [],
            "tags": [],
        }
    else:
        result = None
    return result
    

def extract_page_info(url: str, single_resq_timout: float = 60.) -> List["InfoItem"]:
    
    resp = requests.get(url, timeout=single_resq_timout)
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to fetch  content; {resp.status_code}, {resp.content=}")
    soup = BeautifulSoup(resp.content, "html.parser")
    
    results = []
    paper_overviews = soup.select("div.highwire-article-citation.highwire-citation-type-highwire-article")
    for paper_overview in paper_overviews:
        title = paper_overview.select_one("span.highwire-cite-title").text.strip()
        article_url_suffix = paper_overview.select_one("a.highwire-cite-linked-title").attrs["href"]
        link = f"https://www.biorxiv.org{article_url_suffix}"
        pdf_link = f"https://www.biorxiv.org{article_url_suffix}.full.pdf"
        time_start = datetime.now()
        article_result = extract_article_info(link, single_resq_timout)
        time_end = datetime.now()
        if article_result is None:
            break
        delta_sec = (time_end - time_start).total_seconds()
        sleep_time = max(0, single_resq_timout - delta_sec) * random.uniform(0.1, 0.7)
        article_result["title"] = title
        article_result["links"].append({"biorxiv": link})
        article_result["links"].append({"pdf": pdf_link})
        results.append(article_result)
        time.sleep(sleep_time)
    
    return results

def get_info(url: str, single_resq_timout: float = 10., max_items=100) -> List["InfoItem"]:
    page_num = 0
    results = []  # type: List["InfoItem"]
    while len(results) < max_items:
        page_url = f"{url}?page={page_num}"
        page_results = extract_page_info(page_url, single_resq_timout)
        if len(page_results) < 10:  # no more
            results += page_results
            break  # expired
        page_num += 1

    return results

if __name__ == '__main__':
    url = "https://www.biorxiv.org/collection/biochemistry"
    print(get_info(url, single_resq_timout=15.))
