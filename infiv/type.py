from typing import List, TypedDict, Any, Protocol, TYPE_CHECKING, Literal, Dict

if TYPE_CHECKING:
    from datetime import datetime
    import time

class InfoItem(TypedDict):
    title: str
    links: List[Dict[str, str]]  # list of [text, url]
    content: str  # in markdown format
    pub_datetime: "datetime"
    tags: List[str]

class HandlerFunc(Protocol):
    def __call__(self, url: str, **kwds: Any) -> InfoItem:
        ...

## RSS type from feedparser

class RSSEntryDict(TypedDict):
    title: str
    title_detail: dict
    summary: str
    summary_detail: dict
    links: List[dict]
    link: str
    id: str
    guidislink: bool
    published: str
    published_parsed: "time.struct_time"

class RSSFeedDict(TypedDict):
    ## the dict from feedparser or attributes for the whole pages title, link and etc
    title: str
    title_detail: dict
    links: List[dict]
    link: str
    subtitle: str
    subtitle_detail: dict
    generator: str
    generator_detail: dict
    publisher: str
    publisher_detail: dict
    language: str
    updated: str
    updated_parsed: "time.struct_time"
    ttl: str

class RSSPageDict(TypedDict):
    bozo: bool  # False means a well-formatted xml from the rss feed; True for thing wrong
    entries: List[RSSEntryDict]
    feed: RSSFeedDict
    headers: dict
    encoding: Literal["utf-8"]
    version: Literal["rss090", "rss091n", "rss091u", "rss092", "rss093", "rss094", "rss20", "rss10", "rss", "atom01", "atom02", "atom03", "atom10", "atom", "cdf", "json1"]
    namespaces: dict
