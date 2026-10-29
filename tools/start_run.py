from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.scrapely_api import call, json_object, resource_id, run_summary


class StartRunTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        actor = resource_id(tool_parameters.get("actor_id"), "actor_id")
        run_input = json_object(tool_parameters.get("input"), "input")
        res = call(self.runtime.credentials.get("scrapely_api_key", ""), "POST", f"/v2/actors/{actor}/runs", body=run_input)
        yield self.create_json_message(run_summary((res or {}).get("data") or {}))
