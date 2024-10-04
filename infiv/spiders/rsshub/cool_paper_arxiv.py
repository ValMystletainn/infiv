from typing import TYPE_CHECKING, List

import feedparser
import requests
from bs4 import BeautifulSoup

from infiv.utils import strcut_time_to_datetime

if TYPE_CHECKING:
    from infiv.type import InfoItem, RSSPageDict


def _extract_abstract(rss_summary: str) -> str:
    soup = BeautifulSoup(rss_summary, "html.parser")
    paragraphs = soup.find_all("p")
    abstract = '\n\n'.join([p.text for p in paragraphs])  # to a single markdown
    return abstract

def get_info(url: str) -> List["InfoItem"]:
    resp = requests.get(url, timeout=60)
    if resp.status_code != 200:
        raise RuntimeError("Failed to fetch rsshub cool papers arxiv content")
    content = feedparser.parse(resp.content)  # type: RSSPageDict

    ##
    info_items = []  # type: List["InfoItem"]
    for entry in content["entries"]:
        title = entry["title"]
        abstract = _extract_abstract(entry["summary"])
        link = entry["link"]
        # extract arxiv number
        arxiv_number = link.split("/")[-1]
        abs_link = f"https://arxiv.org/abs/{arxiv_number}"
        html_link = f"https://arxiv.org/html/{arxiv_number}"
        pdf_link = f"https://arxiv.org/pdf/{arxiv_number}"
        kimi_link = f"https://papers.cool/arxiv/{arxiv_number}"
        pub_datetime = strcut_time_to_datetime(entry["published_parsed"])
        tags = []
        info_item = {
            "title": title,
            "content": abstract,
            "links": [
                {"arxiv": abs_link},
                {"html": html_link},
                {"pdf": pdf_link},
                {"kimi": kimi_link},
            ],
            "pub_datetime": pub_datetime,
            "tags": tags
        }  # type: InfoItem
        info_items.append(info_item)

    return info_items


if __name__ == "__main__":
    import os
    from urllib.parse import urljoin

    from pprint import pprint
    for subject in ["cs.AI", "math.NT"]:  # use math.NT to check latex formula extract
        rsshub_url = os.environ.get("RSSHUB_URL", "https://rsshub.app/")
        rsshub_url = urljoin(rsshub_url, f"papers/arxiv/{subject}")
        print(f"visiting {rsshub_url}")
        items = get_info(rsshub_url)
        print(f"{subject=}")
        pprint(items[-1])
        print()
