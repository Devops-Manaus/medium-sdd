from ddgs import DDGS

class SearchTool:
    def search(self, query: str, num: int = 8) -> list[dict]:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=num):
                results.append({
                    "title":   r.get("title", ""),
                    "url":     r.get("href", ""),
                    "snippet": r.get("body", "")
                })
        return results

    def search_multi(self, queries: list[str]) -> dict[str, list]:
        return {q: self.search(q) for q in queries}

    def save_urls(self, results_by_query: dict, path: str):
        import os
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            for query, results in results_by_query.items():
                f.write(f"\n## Query: {query}\n")
                for r in results:
                    f.write(f"- {r['url']}\n")