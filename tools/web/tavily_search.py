from langchain_tavily import TavilySearch
from pydantic import BaseModel
from langchain_core.tools import tool

class SearchResult(BaseModel):
    title: str
    url: str
    content: str

class SearchOutput(BaseModel):
    results: list[SearchResult]

_tavily = None

@tool
def tavily_search(query: str) -> dict:
    """搜索实时互联网信息，并返回结构化搜索结果。"""
    global _tavily
    if _tavily is None:
        _tavily = TavilySearch(max_results=5, include_answer=False)
    raw_result = _tavily.invoke({"query": query})

    results = [
        SearchResult(
            title=item["title"],
            url=item["url"],
            content=item["content"],
        )
        for item in raw_result["results"]
    ]

    output = SearchOutput(results=results)
    return output.model_dump()