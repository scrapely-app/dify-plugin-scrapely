from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.scrapely_api import ScrapelyError, call, whole_number


class SearchActorsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        query = str(tool_parameters.get("query") or "").strip()
        if not query:
            raise ScrapelyError("query is required.")
        limit = whole_number(tool_parameters.get("limit"), "limit", 10, 1, 50)
        res = call(self.runtime.credentials.get("scrapely_api_key", ""), "GET", "/v2/store", params={"search": query, "limit": limit})
        actors = [
            {
                "id": f"{a.get('username')}/{a.get('name')}",
                "title": a.get("title"),
                "description": a.get("description"),
                "users_30_days": (a.get("stats") or {}).get("totalUsers30Days"),
            }
            for a in ((res or {}).get("data") or {}).get("items") or []
            if isinstance(a, dict)
        ]
        yield self.create_json_message({"actors": actors, "count": len(actors)})
