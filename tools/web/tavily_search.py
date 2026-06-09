from langchain_tavily import TavilySearch
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_tavily import TavilySearch

class SearchResult(BaseModel):
    title: str
    url: str
    content: str

class SearchOutput(BaseModel):
    results: list[SearchResult]

tavily = TavilySearch(
    max_results=5,
    include_answer=False,
)

@tool
def tavily_search(query: str) -> dict:
    """搜索实时互联网信息，并返回结构化搜索结果。"""
    raw_result = tavily.invoke({"query": query})

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