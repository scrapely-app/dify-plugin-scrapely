from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.scrapely_api import DEFAULT_HTTP_TIMEOUT, call, resource_id, run_summary, whole_number


class GetRunTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        run = resource_id(tool_parameters.get("run_id"), "run_id")
        wait = whole_number(tool_parameters.get("wait_seconds"), "wait_seconds", 0, 0, 60)
        res = call(
            self.runtime.credentials.get("scrapely_api_key", ""),
            "GET",
            f"/v2/actor-runs/{run}",
            params={"waitForFinish": wait} if wait else None,
            timeout=DEFAULT_HTTP_TIMEOUT + wait,
        )
        yield self.create_json_message(run_summary((res or {}).get("data") or {}))
