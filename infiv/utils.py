from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime
    import time


def strcut_time_to_datetime(struct_time: "time.struct_time") -> "datetime":
    from datetime import datetime
    return datetime(
        year=struct_time.tm_year,
        month=struct_time.tm_mon,
        day=struct_time.tm_mday,
        hour=struct_time.tm_hour,
        minute=struct_time.tm_min,
        second=struct_time.tm_sec,
    )

def html_to_info_item_markdown(html: str) -> str:
    """
    info item markdown means:
    1. remove all head tag, replace it as a bold text
    2. remove all the base64 image
    """
    import re
    from markdownify import markdownify as md

    img_pattern = re.compile(r'<img\s+[^>]*src=["\']data:image/[^"\']*["\'][^>]*alt=["\']([^"\']*)["\'][^>]*>', re.IGNORECASE)
    html = img_pattern.sub(lambda m: f'image: {m.group(1)}', html)

    markdown = md(html, heading_style="ATX")
    
    # handle the 
    lines = markdown.splitlines()
    for i, line in enumerate(lines):
        if line.startswith('#'):  # 检查是否是标题
            # 去掉标题的 '#' 和空格，并加粗
            title_text = line.lstrip('#').strip()
            lines[i] = f"**{title_text}**"  # 加粗标题
    
    return "\n".join(lines)
