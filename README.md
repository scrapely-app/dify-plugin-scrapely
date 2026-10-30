# Scrape.ly

[Scrape.ly](https://scrape.ly) turns websites into structured data. This plugin lets Dify workflows and agents scrape web pages and run Scrape.ly Actors (ready-made scrapers) and tasks, then use their results.

## Setup

1. Create an API key in the [Scrape.ly dashboard](https://my.scrape.ly/settings/api) under **Settings → API & Integrations**.
2. In Dify, open **Integrations → Tools**, select Scrape.ly, and add the key as its credentials.

## Tools

| Tool | What it does |
| --- | --- |
| **Scrape website** | Scrapes a web page (and optionally up to 20 linked pages) into title, text and markdown. |
| **Run Actor** | Runs an Actor with a JSON input, waits for it to finish and returns its results. |
| **Run task** | Runs a saved task (optionally overriding its input) and returns its results. |
| **Start run** | Starts an Actor run without waiting, for runs that take longer than 5 minutes. |
| **Get run** | Checks a run's status, optionally waiting up to 45 seconds for it to finish. |
| **Get dataset items** | Reads the results stored in a dataset, for example from an earlier run. |
| **Search Actors** | Finds ready-made scrapers (Actors) in the Scrape.ly Store by keyword. |

**Run Actor** and **Run task** wait up to 5 minutes. For longer runs, use **Start run**, check it with **Get run**, then read its results with **Get dataset items** and the run's `dataset_id`.

Runs use your Scrape.ly account's balance, like runs started anywhere else. See [pricing](https://scrape.ly/pricing).

## Connection

The plugin connects to the Scrape.ly API at `https://api.scrape.ly` over HTTPS, authenticated with your API key. It needs no other network access and nothing to host yourself; the scraping runs on Scrape.ly.

## Links

- [Docs](https://scrape.ly/docs/dify)
- [API reference](https://scrape.ly/docs/api)
- [Source repository](https://github.com/scrapely-app/dify-plugin-scrapely)
- Support: hello@scrape.ly
