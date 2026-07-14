"""Minimal Socrata SODA API client: paginated GET over `$limit`/`$offset`.

No authentication is required to read this dataset at its current volume — an
app token (if set) only raises Socrata's anonymous throttling ceiling.
"""

import requests

from src import config

PAGE_SIZE = 50000


def get_paginated(resource_url: str, params: dict | None = None) -> list[dict]:
    """Follows `$limit`/`$offset` until a short page signals the last one."""
    headers = {"X-App-Token": config.SOCRATA_APP_TOKEN} if config.SOCRATA_APP_TOKEN else {}
    query = dict(params or {}, **{"$limit": PAGE_SIZE, "$order": ":id"})

    rows: list[dict] = []
    offset = 0
    while True:
        response = requests.get(resource_url, headers=headers, params={**query, "$offset": offset})
        response.raise_for_status()
        page = response.json()
        rows.extend(page)

        if len(page) < PAGE_SIZE:
            break
        offset += PAGE_SIZE

    return rows