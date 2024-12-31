import pandas as pd

from ..generate_calendar import (
    df_calendar,
    generate_html_table,
    sheet_calendar,
    sheet_id,
    url_calendar,
)


def test_calendar_google_sheet():
    """Check that the id, sheet, and URL are correct."""
    assert sheet_id == "1SO2i9TXqQL9wSFTjE-GLRONtXmXfvcQ5kYckTm6fY4M"
    assert sheet_calendar == "calendar"
    assert url_calendar == (
        f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/"
        f"tq?tqx=out:csv&sheet={sheet_calendar}"
    )


def test_calendar_dataframe():
    """Check that the loaded dataframe contains the expected information to build the
    HTML page.
    """
    expected_columns = [
        "Date",
        "Durée organisation",
        "Course",
        "Type de course",
        "Longeur circuit",
        "Catégories",
        "Club",
        "Affiche",
        "Résultats TC",
        "Résultats école",
    ]
    for col in expected_columns:
        assert (
            col in df_calendar.columns
        ), f"Column {col} is missing in the calendar dataframe"

    assert pd.api.types.is_datetime64_any_dtype(
        df_calendar["Date"]
    ), "The 'Date' column should be a datetime object"
    assert df_calendar["Date"].dt.year.unique() == [2025], "The year should be 2025"

    expected_duration = ("Demi-journée", "Journée complète")
    for duration in df_calendar["Durée organisation"].unique():
        if pd.isna(duration):
            continue
        assert (
            duration in expected_duration
        ), f"Unexpected duration: {duration}. Should be one of {expected_duration}"
