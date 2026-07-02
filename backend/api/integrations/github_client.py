import httpx


class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: str | None = None) -> None:
        self._headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "AI-Talent-Sense",
        }
        if token:
            self._headers["Authorization"] = f"Bearer {token}"

    def search_users(self, query: str, per_page: int = 10) -> list[dict[str, object]]:
        response = httpx.get(
            f"{self.BASE_URL}/search/users",
            headers=self._headers,
            params={"q": query, "per_page": per_page},
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()
        items = data.get("items", []) or []
        return [
            {
                "login": item.get("login", ""),
                "url": item.get("html_url", item.get("url", "")),
                "score": item.get("score", 0),
            }
            for item in items
        ]

    def get_user(self, username: str) -> dict[str, object]:
        response = httpx.get(
            f"{self.BASE_URL}/users/{username}",
            headers=self._headers,
            timeout=10.0,
        )
        response.raise_for_status()
        return response.json()

    def get_repositories(self, username: str, per_page: int = 5) -> list[dict[str, object]]:
        response = httpx.get(
            f"{self.BASE_URL}/users/{username}/repos",
            headers=self._headers,
            params={"per_page": per_page, "sort": "updated", "direction": "desc"},
            timeout=10.0,
        )
        response.raise_for_status()
        return response.json()
