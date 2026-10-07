"""Identify Ashby boards and retrieve their published jobs."""

import json
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen


def find_board_identifiers(search_results):
    identifiers = []
    for result in search_results:
        url = urlsplit(result["url"])
        path = url.path.strip("/")
        if url.hostname == "jobs.ashbyhq.com" and path:
            identifier = path.split("/")[0]
            if identifier not in identifiers:
                identifiers.append(identifier)
    return identifiers


def fetch_jobs(board_identifier):
    url = f"https://api.ashbyhq.com/posting-api/job-board/{quote(board_identifier, safe='')}"
    request = Request(url, headers={
        "User-Agent": "job-search-agent/0.1",
        "Accept": "application/json",
    })
    with urlopen(request, timeout=30) as response:
        board = json.load(response)

    jobs = []
    for posting in board["jobs"]:
        if posting.get("isListed") is False:
            continue
        locations = [posting.get("location", "")]
        for location in posting.get("secondaryLocations", []):
            locations.append(location.get("location", ""))
        jobs.append({
            "posting_id": urlsplit(posting["jobUrl"]).path.rstrip("/").split("/")[-1],
            "title": posting["title"],
            "location": "; ".join(filter(None, locations)),
            "url": posting["jobUrl"],
            "description": posting.get("descriptionPlain", ""),
            "description_html": posting.get("descriptionHtml", ""),
        })
    return jobs
