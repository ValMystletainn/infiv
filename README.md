# infiv

infiv is a python automation project to make a customized and all-in-one newspaper with source links.

infiv means the infinite information archives.

## Highlight

1. Customizable. You can choose the infomation sources you like. And you can replace any components of the project as you like, for example, replace the LLM embedder, add a brand new process function to deal with your private data sources.
2. Help you escaping the information bubble, bias and addictive pull-to-refresh. You should actively choose the information source you want when using this pages, which means you can control it by yourself rather than the recommendation system of the apps.
3. Merge the similar information from different sources into one page. This will help you to avoid the redundancy infomration acquisition and biased infomation.

## Usage

We use modern python packaging style -- all information in the `pyproject.toml`.

To prepare the dependencies and optional dependencies for the project, you can install the project in editable mode:
```base
pip install -e .
## or add some other optional dependencies if you want to use some special features, for example
## pip install -e .[rss, crawl4ai]
## will install the optional dependencies to parse rss site to markdown and use the package crawl4ai to convert the html to markdown.
## If you don't want this package be a visible in your current python environment, you can install it to get the all dependency and then uninstall it by
## pip uninstall infiv
```

## TODO

- [ ] add a function to call the text to image model to make a banner.
- [ ] init rsshub instance as git submodule in the action rather than using the public one.
- [ ] add the support from crawl4ai.
- [ ] As a python pypi upload or focus on a script and move most of get information parts to rsshub and rsshub patch
- [ ] auto email, telegram, wechat, etc.
