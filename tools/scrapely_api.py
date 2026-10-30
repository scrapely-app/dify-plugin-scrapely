"""Calls to the Scrape.ly API (https://scrape.ly/docs/api) shared by the tools."""

import json
import os
import time
from typing import Any
from urllib.parse import quote

import requests

# SCRAPELY_API_URL points a local debug run at another environment (e.g. staging).
API_URL = os.environ.get("SCRAPELY_API_URL", "https://api.scrape.ly").rstrip("/")
# Bump with the version in manifest.yaml.
USER_AGENT = "dify-plugin-scrapely/0.0.1"

DEFAULT_HTTP_TIMEOUT = 60
# The API holds a request open at most 45 s, so a run is started and then
# polled until it finishes, for up to RUN_WAIT_SECS (main.py allows 360 s).
POLL_WAIT_SECS = 45
RUN_WAIT_SECS = 300
FINISHED_STATUSES = {"SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"}
MAX_ITEMS_LIMIT = 1000

# Scrapes one website into title, text and markdown (Scrape website tool).
WEBSITE_CRAWLER = "querystone~website-content-crawler"


class ScrapelyError(Exception):
    pass


def call(token: str, method: str, path: str, *, params: dict | None = None, body: Any = None, timeout: int = DEFAULT_HTTP_TIMEOUT) -> Any:
    if not token:
        raise ScrapelyError("Add your Scrape.ly API key in the plugin settings.")
    try:
        res = requests.request(
            method,
            f"{API_URL}{path}",
            headers={"Authorization": f"Bearer {token}", "User-Agent": USER_AGENT},
            params=params,
            json=body,
            timeout=timeout,
        )
    except requests.Timeout as e:
        raise ScrapelyError("Scrape.ly did not answer in time. Try again, or use a smaller input.") from e
    except requests.RequestException as e:
        raise ScrapelyError(f"Could not reach Scrape.ly: {e}") from e
    if res.status_code >= 400:
        message = ""
        try:
            message = (res.json().get("error") or {}).get("message") or ""
        except ValueError:
            pass
        if res.status_code == 401:
            raise ScrapelyError("The Scrape.ly API key is not valid. Create one under Settings → API & Integrations in the Scrape.ly dashboard.")
        raise ScrapelyError(f"Scrape.ly returned HTTP {res.status_code}{f': {message}' if message else ''}")
    return res.json() if res.content else None


def resource_id(value: Any, name: str) -> str:
    """An Actor, task or dataset ID; `username/name` becomes `username~name` as the API expects."""
    text = str(value or "").strip()
    if not text:
        raise ScrapelyError(f"{name} is required.")
    return quote(text.replace("/", "~"), safe="~")


def json_object(value: Any, name: str) -> dict:
    """A JSON object given as text (empty = {})."""
    if value is None or value == "":
        return {}
    if isinstance(value, dict):
        return value
    try:
        parsed = json.loads(str(value))
    except ValueError as e:
        raise ScrapelyError(f"{name} must be a JSON object, for example {{\"startUrls\": [{{\"url\": \"https://example.com\"}}]}}.") from e
    if not isinstance(parsed, dict):
        raise ScrapelyError(f"{name} must be a JSON object.")
    return parsed


def whole_number(value: Any, name: str, default: int, minimum: int, maximum: int) -> int:
    if value is None or value == "":
        return default
    try:
        number = int(float(value))
    except (TypeError, ValueError, OverflowError) as e:
        raise ScrapelyError(f"{name} must be a whole number.") from e
    return max(minimum, min(maximum, number))


def run_and_wait(token: str, path: str, run_input: dict, max_items: int) -> list:
    """Run an Actor or task, wait for it (up to 5 minutes) and return its results."""
    run = (call(token, "POST", f"{path}/runs", body=run_input) or {}).get("data") or {}
    run_id = run.get("id")
    if not run_id:
        raise ScrapelyError("Scrape.ly did not return the started run.")
    deadline = time.monotonic() + RUN_WAIT_SECS
    while run.get("status") not in FINISHED_STATUSES:
        left = int(deadline - time.monotonic())
        if left <= 0:
            raise ScrapelyError(
                f"Run {run_id} is still running after 5 minutes. Check it with Get run, "
                f"then read its results with Get dataset items (dataset {run.get('defaultDatasetId')})."
            )
        wait = min(POLL_WAIT_SECS, left)
        run = (call(token, "GET", f"/v2/actor-runs/{run_id}", params={"waitForFinish": wait}, timeout=DEFAULT_HTTP_TIMEOUT + wait) or {}).get("data") or {}
    if run.get("status") != "SUCCEEDED":
        message = run.get("statusMessage")
        raise ScrapelyError(f"Run {run_id} {run.get('status')}{f': {message}' if message else ''}")
    items = call(token, "GET", f"/v2/datasets/{run.get('defaultDatasetId')}/items", params={"limit": max_items, "clean": "true"})
    return items if isinstance(items, list) else []


def run_summary(run: dict) -> dict:
    """The run fields a workflow needs: its status and where its results are."""
    return {
        "id": run.get("id"),
        "status": run.get("status"),
        "status_message": run.get("statusMessage"),
        "actor_id": run.get("actId"),
        "dataset_id": run.get("defaultDatasetId"),
        "started_at": run.get("startedAt"),
        "finished_at": run.get("finishedAt"),
        "cost_usd": run.get("usageTotalUsd"),
    }
