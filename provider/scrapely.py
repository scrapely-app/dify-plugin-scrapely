from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from tools.scrapely_api import ScrapelyError, call


class ScrapelyProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            call(credentials.get("scrapely_api_key", ""), "GET", "/v2/users/me")
        except ScrapelyError as e:
            raise ToolProviderCredentialValidationError(str(e)) from e
