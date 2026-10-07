"""SQLite storage for discovered employer boards and their job postings."""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def reset_database(path):
    """Discard development data and recreate only the current tables."""
    Path(path).unlink(missing_ok=True)
    connection = open_database(path)
    connection.close()


def open_database(path):
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript("""
        CREATE TABLE IF NOT EXISTS employer_boards (
            id INTEGER PRIMARY KEY,
            provider TEXT NOT NULL,
            identifier TEXT NOT NULL,
            board_url TEXT NOT NULL,
            discovery_city TEXT,
            last_checked TEXT,
            UNIQUE(provider, identifier)
        );
        CREATE TABLE IF NOT EXISTS job_postings (
            board_id INTEGER REFERENCES employer_boards(id),
            posting_id TEXT NOT NULL,
            title TEXT NOT NULL,
            location TEXT,
            url TEXT,
            description TEXT,
            description_html TEXT,
            first_seen TEXT,
            last_seen TEXT,
            PRIMARY KEY(board_id, posting_id)
        );
    """)
    return connection


def save_board_jobs(path, provider, identifier, board_url, city, jobs):
    timestamp = datetime.now(timezone.utc).isoformat()
    connection = open_database(path)
    try:
        connection.execute("""
            INSERT INTO employer_boards
                (provider, identifier, board_url, discovery_city, last_checked)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(provider, identifier) DO UPDATE SET
                board_url=excluded.board_url,
                discovery_city=excluded.discovery_city,
                last_checked=excluded.last_checked
        """, (provider, identifier, board_url, city, timestamp))
        board = connection.execute("""
            SELECT id FROM employer_boards WHERE provider=? AND identifier=?
        """, (provider, identifier)).fetchone()

        for job in jobs:
            connection.execute("""
                INSERT INTO job_postings
                    (board_id, posting_id, title, location, url, description,
                     description_html, first_seen, last_seen)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(board_id, posting_id) DO UPDATE SET
                    title=excluded.title,
                    location=excluded.location,
                    url=excluded.url,
                    description=excluded.description,
                    description_html=excluded.description_html,
                    last_seen=excluded.last_seen
            """, (
                board["id"], job["posting_id"], job["title"], job["location"],
                job["url"], job["description"], job["description_html"],
                timestamp, timestamp,
            ))
        connection.commit()
    finally:
        connection.close()


def list_jobs(path):
    connection = open_database(path)
    try:
        rows = connection.execute("""
            SELECT boards.provider, boards.identifier, jobs.*
            FROM job_postings AS jobs
            JOIN employer_boards AS boards ON boards.id = jobs.board_id
            ORDER BY jobs.last_seen DESC, boards.identifier, jobs.title
        """).fetchall()
    finally:
        connection.close()
    return [dict(row) for row in rows]

