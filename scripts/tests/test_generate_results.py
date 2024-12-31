from ..generate_calendar import (
    SHEET_CALENDAR,
    SHEET_ID,
    URL_CALENDAR,
)


def test_calendar_google_sheet():
    """Check that the id, sheet, and URL are correct."""
    assert SHEET_ID == "1SO2i9TXqQL9wSFTjE-GLRONtXmXfvcQ5kYckTm6fY4M"
    assert SHEET_CALENDAR == "calendar"
    assert URL_CALENDAR == (
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/"
        f"tq?tqx=out:csv&sheet={SHEET_CALENDAR}"
    )
