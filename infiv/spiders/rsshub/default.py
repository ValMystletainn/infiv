from typing import TYPE_CHECKING, List

import feedparser
import requests

from infiv.utils import strcut_time_to_datetime, html_to_info_item_markdown

if TYPE_CHECKING:
    from infiv.type import InfoItem, RSSPageDict

def get_info(url: str) -> List["InfoItem"]:
    resp = requests.get(url, timeout=60)
    if resp.status_code != 200:
        raise RuntimeError("Failed to fetch rsshub content")
    content = feedparser.parse(resp.content)  # type: RSSPageDict
    
    return [
        {
            "title": entry["title"],
            "content": html_to_info_item_markdown(entry["summary"]),
            "links": [
                {"src": entry["link"]},
                {"root src": content["feed"]["link"]},
            ],
            "pub_datetime": strcut_time_to_datetime(entry["published_parsed"]),
            "tags": [],
        }
        for entry in content["entries"]
    ]

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
