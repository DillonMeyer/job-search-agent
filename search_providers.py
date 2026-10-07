"""Search adapters. Both return dictionaries with title, url, and snippet."""

import json
import os
import urllib.request


def search_duckduckgo(query):
    from ddgs import DDGS

    search_client = DDGS(timeout=30)
    search_results = search_client.text(
        query, region="us-en", max_results=10, backend="duckduckgo"
    )

    leads = []
    for result in search_results:
        if not result["href"].strip():
            continue
        leads.append({
            "title": result["title"],
            "url": result["href"],
            "snippet": result.get("body", ""),
        })
    return leads


def search_serper(query):
    api_key = os.environ["SERPER_API_KEY"]

    payload = {"q": query, "gl": "us", "hl": "en", "num": 10}
    request = urllib.request.Request(
        "https://google.serper.dev/search",
        data=json.dumps(payload).encode(),
        headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        search_results = json.load(response)

    leads = []
    for result in search_results["organic"][:10]:
        leads.append({
            "title": result["title"],
            "url": result["link"],
            "snippet": result.get("snippet", ""),
        })
    return leads
