from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.scrapely_api import MAX_ITEMS_LIMIT, json_object, resource_id, run_and_wait, whole_number


class RunTaskTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        task = resource_id(tool_parameters.get("task_id"), "task_id")
        run_input = json_object(tool_parameters.get("input"), "input")
        max_items = whole_number(tool_parameters.get("max_items"), "max_items", 100, 1, MAX_ITEMS_LIMIT)
        items = run_and_wait(self.runtime.credentials.get("scrapely_api_key", ""), f"/v2/actor-tasks/{task}", run_input, max_items)
        yield self.create_json_message({"items": items, "count": len(items)})
