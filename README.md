# Job Search Agent

Current flow: city-based Ashby search → unique board identifiers → public API retrieves jobs → broad title filter → SQLite saves boards and matching postings. No LLM calls yet.

## Code map

- `search.py`: builds city queries and coordinates search, retrieval, and saving.
- `search_providers.py`: interchangeable Serper/DDG searches.
- `ashby.py`: extracts identifiers from URLs and retrieves published jobs.
- `sqlite_storage.py`: stores boards and postings; repeat postings update existing rows.

## Run

```sh
uv run python search.py
uv run python view_jobs.py
```

Edit `CITY` and `SEARCH_PROVIDER` in `search.py`. Serper is selected and reads `SERPER_API_KEY` from `.env` automatically. DDG needs no key. Dependencies live in `pyproject.toml` and `uv.lock`.

A run searches Ashby pages for the city with `"AI engineer"` and `"software engineer"` separately. Edit `SEARCH_TERMS` to change these. There are two search-provider calls, up to ten results each. Duplicate board identifiers are combined before fetching, so each board is fetched once per run (at most twenty boards).

Ashby calls use no Serper credits. Python keeps titles matching the editable `JOB_TITLE_TERMS` in `search.py`, ignoring case and treating hyphens as spaces. This deliberately broad filter can retain irrelevant roles and miss unusual titles. Seniority, location, skills, and experience are not filtered yet. Each board prints fetched/kept counts. A failed fetch raises a Python error, not an empty successful check.

## Data

- `employer_boards`: provider, identifier, board URL, latest discovery city, last successful check.
- `job_postings`: board reference, posting ID, title, actual location(s), URL, descriptions, first/last seen.

Development mode: every search run deletes the database and recreates the two current tables before searching. Only that run’s collected postings remain, including partial results if retrieval fails. `view_leads.py` also shows current postings.

The discovery city does not establish job location. Live data and credentials stay out of Git.

## Next

- Review the discovered boards and retrieved postings.
- Review title filtering, then actual locations and local LLM extraction of hard skills/YOE.
- Later: industry-based searches restricted to ATS domains, city rotation, Greenhouse/Lever, and AI-search comparison.
- Keep changes small and readable. Tests remain deferred until requested.
