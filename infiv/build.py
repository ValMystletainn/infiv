import functools
import importlib
import inspect
import itertools
import logging
import random
import time
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, Callable, List
from datetime import datetime

import yaml

if TYPE_CHECKING:
    import argparse

    from infiv.types import InfoItem

logger = logging.getLogger(__name__)


def bind_params(func, kwargs_dict):
    # Get the function signature
    sig = inspect.signature(func)
    func_name = func.__name__

    # Separate required parameters and optional parameters (those with default values)
    required_params = []
    optional_params = []

    for param_name, param in sig.parameters.items():
        if param.default == inspect.Parameter.empty and param.kind in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        ):
            required_params.append(param_name)
        else:
            optional_params.append(param_name)

    # Check if required parameters are missing in kwargs
    missing_required = []
    bound_args = {}

    for param in required_params:
        if param in kwargs_dict:
            bound_args[param] = kwargs_dict[param]
        else:
            missing_required.append(param)

    # Bind optional parameters if available in kwargs
    for param in optional_params:
        if param in kwargs_dict:
            bound_args[param] = kwargs_dict[param]

    # Log if there are unused kwargs
    unused_kwargs = set(kwargs_dict) - set(required_params) - set(optional_params)
    if unused_kwargs:
        for unused in unused_kwargs:
            logger.warning(f"Unused kwargs: {unused} in func {func_name}")

    # Raise an error if any required arguments are missing
    if missing_required:
        raise TypeError(
            f"Missing required arguments: {', '.join(missing_required)} for func {func_name}"
        )

    # Use functools.partial to bind the provided arguments to the function
    partial_func = functools.partial(func, **bound_args)
    return partial_func


def import_function_by_full_path(full_path: str):
    # Split the full path into module path and function name
    module_path, function_name = full_path.rsplit(".", 1)

    # Import the module by the module path
    module = importlib.import_module(module_path)

    # Get the function from the module
    func = getattr(module, function_name)

    return func


def retry_with_timeout_decorator(
    max_retries: int = 3,
    base_delay: int = 10,
    factor: int = 2,
    jitter: bool = True,
):
    """
    A retry decorator with exponentially increasing timeout.

    :param max_retries: Maximum number of retries
    :param base_delay: Base delay time in seconds
    :param factor: Factor by which to increase the delay
    :param jitter: If True, add jitter to the delay
    :return: the decorator that wraps the function
    """

    def decorator(func: Callable[[], List["InfoItem"]]) -> Callable[[], List["InfoItem"]]:

        @functools.wraps(func)
        def retry_calling() -> List["InfoItem"]:
            retries = 0
            while retries < max_retries:
                try:
                    # Compute the current delay
                    delay = base_delay * (factor**retries)
                    if jitter:
                        delay += random.uniform(0, 1)  # Add jitter

                    # If the function accepts 'timeout', bind the computed delay
                    sig = inspect.signature(func)
                    if (
                        "timeout" in sig.parameters
                        and sig.parameters["timeout"].default is None
                    ):
                        return func(timeout=delay)
                    else:
                        return func()
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        url = sig.parameters.get("url", "bad url")
                        return [
                            {
                                "title": url,
                                "content": f"fail to fetch, please visited the url manually.",
                                "links": [{"source": url}],
                                "pub_datetime": datetime.now(),
                                "tags": [],
                            }
                        ]
                    logger.info(
                        f"Fail in the try {retries}/{max_retries} in {delay:.2f} seconds..."
                    )
                    if not (
                        "timeout" in sig.parameters
                        and sig.parameters["timeout"].default is None
                    ):
                        ## only sleep if no timeout
                        time.sleep(delay)

        return retry_calling

    return decorator


def main(args: "argparse.Namespace"):
    src_config = args.src_config
    with open(src_config, "r") as f:
        src_config_data = yaml.load(f, Loader=yaml.FullLoader)
    max_thread = getattr(args, "threads", 4)

    ## 1. fetch data
    sources = src_config_data["sources"]
    fetch_funcs = [
        bind_params(
            import_function_by_full_path(source["func"]),
            {"url": source.get("url", ""), **source.get("kwargs", {})},
        )
        for source in sources
    ]

    retry_settting = src_config_data.get("retry", {})
    fetch_funcs = [
        retry_with_timeout_decorator(
            max_retries=retry_settting.get("max_retries", 3),
            base_delay=retry_settting.get("base_delay", 10),
            factor=retry_settting.get("factor", 2),
            jitter=retry_settting.get("jitter", True),
        )(func)
        for func in fetch_funcs
    ]

    with ThreadPoolExecutor(max_workers=max_thread) as executor:
        fetch_results = list(executor.map(lambda func: func(), fetch_funcs))  # type: List[List["InfoItem"]]

    ## flatten the fetch results
    flattened_results = []  # type: List["InfoItem"]
    for fetch_result, source in zip(fetch_results, sources):
        subject = source.get("subject", "unclass")  # type: str
        for item in fetch_result:
            item["subject"] = subject
        flattened_results += fetch_result

    ## 2. get embedding from google gemini
    if not getattr(args, "use_embed", False):
        embeddings = None
    else:
        import os

        import google.generativeai as genai

        genai.configure(transport="rest")  # TODO: test speed https vs grpc
        get_embedding_funcs = [
            functools.partial(
                genai.embed_content,
                model="models/embedding-001",
                content=item["title"],
                task_type="clustering",
            )
            for item in flattened_results
        ]
        get_embedding_funcs = [
            retry_with_timeout_decorator(
                max_retries=3,
                base_delay=60 / 1200,  # 1500 RPM at peak
                factor=2,
                jitter=True,
            )(func)
            for func in get_embedding_funcs
        ]  # TODO: a bit abuse, refactor it or retry decorator. since the retry decorator typing to return a function return List[ItemInfo]

        with ThreadPoolExecutor(max_workers=max_thread) as executor:
            embeddings = list(executor.map(lambda func: func(), get_embedding_funcs))
        
        embeddings = [e_dict["embedding"] for e_dict in embeddings]
    ## 3. output markdown
    ### TODO: dump to jinja2 template markdown
    n = len(flattened_results)
    ## result md
    md_sections = [
        f"# Daily News\n\nGenerated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} \n\nWe have {n} news from different sources."
    ]
    subject_group_indices = list(range(n))
    subject_group_indices.sort(key=lambda i: flattened_results[i]["subject"])
    for subject, indices in itertools.groupby(
        subject_group_indices, key=lambda i: flattened_results[i]["subject"]
    ):
        md_sections.append(f"## {subject}")
        for index in indices:
            item = flattened_results[index]
            section_content = f"### {item['title']}"
            ## insert links
            section_content += "\n"
            for i, link in enumerate(item["links"]):
                if isinstance(link, str):
                    section_content += f"[{link}]({link}); "
                elif isinstance(link, dict):
                    alt_text = next(iter(link.keys()))
                    section_content += f"[{alt_text}]({link[alt_text]})"
                
                if i < len(item["links"]) - 1:
                    section_content += " "
            ## insert time
            section_content += f"\n\n{item['pub_datetime'].strftime(r'%Y/%m/%d %H:%M')} GTM"
            
            ## insert content
            section_content += "\n\n"
            content = item["content"]
            if len(content) >= 5000:
                content = content[:5000] + "..."
            section_content += content

            md_sections.append(section_content)

    ## 4. ai summary if needed
    # TODO:

    ## 5. dump
    with open("output.md", "wt") as f:
        f.write("\n\n".join(md_sections))

    logger.info("Dump result markdown at output.md")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()  # TODO: check this work?
    main(parser.parse_args())
