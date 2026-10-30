from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.scrapely_api import WEBSITE_CRAWLER, ScrapelyError, run_and_wait, whole_number


class ScrapeWebsiteTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        url = str(tool_parameters.get("url") or "").strip()
        if not url.lower().startswith(("http://", "https://")):
            raise ScrapelyError("url must start with http:// or https://.")
        max_pages = whole_number(tool_parameters.get("max_pages"), "max_pages", 1, 1, 20)
        items = run_and_wait(
            self.runtime.credentials.get("scrapely_api_key", ""),
            f"/v2/actors/{WEBSITE_CRAWLER}",
            {"startUrls": [{"url": url}], "maxCrawlPages": max_pages, "saveMarkdown": True, "proxyConfiguration": {}},
            max_pages,
        )
        pages = [
            {
                "url": item.get("url"),
                "title": (item.get("metadata") or {}).get("title"),
                "text": item.get("text"),
                "markdown": item.get("markdown"),
            }
            for item in items
            if isinstance(item, dict)
        ]
        yield self.create_text_message("\n\n---\n\n".join(p["markdown"] or p["text"] or "" for p in pages))
        yield self.create_json_message({"pages": pages, "count": len(pages)})
