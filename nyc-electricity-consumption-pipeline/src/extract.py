"""Pulls raw records from both source APIs as plain lists of dicts."""

from datetime import date

from src import config, nyc_open_data_client, nyiso_client


def extract_nycha_bills() -> list[dict]:
    return nyc_open_data_client.get_paginated(config.NYCHA_RESOURCE_URL)


def extract_nyiso_monthly_load() -> list[dict]:
    current_year_month = date.today().strftime("%Y-%m")
    return nyiso_client.extract_nyiso_monthly_load(end_year_month=current_year_month)


def extract_all() -> dict[str, list[dict]]:
    return {
        "nycha_electric_bills": extract_nycha_bills(),
        "nyiso_monthly_load": extract_nyiso_monthly_load(),
    }
