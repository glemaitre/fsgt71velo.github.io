import pytest

from ..generate_club_listing import (
    SHEET_DIRECTORY,
    SHEET_ID,
    SHEET_LISTING,
    URL_DIRECTORY,
    URL_LISTING,
)


@pytest.mark.parametrize(
    "sheet_id, sheet_name, url, expected_sheet_name",
    [
        (SHEET_ID, SHEET_LISTING, URL_LISTING, "Listing"),
        (SHEET_ID, SHEET_DIRECTORY, URL_DIRECTORY, "Annuaire"),
    ],
)
def test_calendar_google_sheet(sheet_id, sheet_name, url, expected_sheet_name):
    """Check that the id, sheet, and URL are correct."""
    assert sheet_id == "1ocHqS1lCjGVwKTd_ES_L06eOFDN90Jd_Kap3OtZhgVM"
    assert sheet_name == expected_sheet_name
    assert url == (
        f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/"
        f"tq?tqx=out:csv&sheet={sheet_name}"
    )
