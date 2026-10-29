from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.scrapely_api import MAX_ITEMS_LIMIT, call, resource_id, whole_number


class GetDatasetItemsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        dataset = resource_id(tool_parameters.get("dataset_id"), "dataset_id")
        limit = whole_number(tool_parameters.get("limit"), "limit", 100, 1, MAX_ITEMS_LIMIT)
        offset = whole_number(tool_parameters.get("offset"), "offset", 0, 0, 10**9)
        items = call(
            self.runtime.credentials.get("scrapely_api_key", ""),
            "GET",
            f"/v2/datasets/{dataset}/items",
            params={"limit": limit, "offset": offset, "clean": "true"},
        )
        items = items if isinstance(items, list) else []
        yield self.create_json_message({"items": items, "count": len(items)})
