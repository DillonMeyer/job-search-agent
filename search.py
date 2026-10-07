"""Discover Ashby boards by city, then retrieve and save their postings."""

from pathlib import Path

from dotenv import load_dotenv

import sqlite_storage
import ashby
from search_providers import search_duckduckgo, search_serper


CITY = "Boise, ID"
SEARCH_TERMS = ["AI engineer", "software engineer"]
# Broad title phrases to keep. These are separate from our Google queries.
JOB_TITLE_TERMS = [
    "software",
    "ai engineer",
    "ai developer",
    "artificial intelligence",
    "machine learning",
    "llm",
    "solutions engineer",
    "solution engineer",
    "forward deployed",
    "front end",
    "frontend",
    "full stack",
    "fullstack",
    "back end",
    "backend",
    "python engineer",
    "python developer",
]
# SEARCH_PROVIDER = search_duckduckgo
SEARCH_PROVIDER = search_serper
DATABASE_PATH = Path(__file__).parent / "jobs.sqlite"


def find_leads(city, search_provider):
    """Combine search results for both terms in the given city."""
    results = []
    for search_term in SEARCH_TERMS:
        query = f'site:jobs.ashbyhq.com {city} "{search_term}"'
        print(f"Query: {query}")
        query_results = search_provider(query)
        print(f"Returned {len(query_results)} search results.")
        results.extend(query_results)
    return results


def filter_jobs_by_title(jobs):
    """Keep broadly relevant titles, regardless of seniority or location."""
    matching_jobs = []
    for job in jobs:
        title = job["title"].lower().replace("-", " ")
        for title_term in JOB_TITLE_TERMS:
            if title_term in title:
                matching_jobs.append(job)
                break
    return matching_jobs


def main():
    load_dotenv(Path(__file__).parent / ".env")
    sqlite_storage.reset_database(DATABASE_PATH)
    print("Cleared saved data for this development run.")
    results = find_leads(CITY, SEARCH_PROVIDER)
    identifiers = ashby.find_board_identifiers(results)
    print(f"Found {len(identifiers)} distinct Ashby boards.")

    for identifier in identifiers:
        print(f"Fetching Ashby board: {identifier}")
        jobs = ashby.fetch_jobs(identifier)
        matching_jobs = filter_jobs_by_title(jobs)
        board_url = f"https://jobs.ashbyhq.com/{identifier}"
        sqlite_storage.save_board_jobs(
            DATABASE_PATH, "ashby", identifier, board_url, CITY, matching_jobs
        )
        print(f"{identifier}: fetched {len(jobs)} postings; kept {len(matching_jobs)} by title.")


if __name__ == "__main__":
    main()
