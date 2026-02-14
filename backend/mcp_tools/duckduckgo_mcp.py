from duckduckgo_search import DDGS

class DuckDuckGoMCP:
    def __init__(self):
        self.ddgs = DDGS()

    def search_web(self, query: str, max_results: int = 5):
        results = []

        for r in self.ddgs.text(query, max_results=max_results):
            results.append({
                "title": r.get("title"),
                "href": r.get("href"),
                "body": r.get("body")
            })

        return results

duckduckgo_mcp = DuckDuckGoMCP()
