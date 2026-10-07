"""Show the titles, locations, and links of collected job postings."""

from pathlib import Path

from sqlite_storage import list_jobs


def main():
    jobs = list_jobs(Path(__file__).parent / "jobs.sqlite")
    print(f"{len(jobs)} stored postings; not filtered or confirmed still open.")
    for job in jobs:
        print(f"\n{job['identifier']}: {job['title']}")
        print(job["location"])
        print(job["url"])


if __name__ == "__main__":
    main()
