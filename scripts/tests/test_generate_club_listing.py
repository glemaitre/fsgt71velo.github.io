import pandas as pd
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


def test_df_listing():
    """Check the integrity of the listing dataframe."""
    df_listing = pd.read_csv(URL_LISTING)

    expected_columns = (
        "Nom du club",
        "Ville",
        "Président Nom",
        "Président Prénom",
        "Responsable cyclisme Nom",
        "Responsable cyclisme Prénom",
        "Responsable cyclotouriste Nom",
        "Responsable cyclotouriste Prénom",
        "Correspondant VTT Nom",
        "Correspondant VTT Prénom",
        "Correspondant vélos enfants Nom",
        "Correspondant vélos enfants Prénom",
    )
    for column in expected_columns:
        assert column in df_listing.columns, f"Column {column} not found in df_listing"


def test_df_directory():
    """Check the integrity of the directory dataframe."""
    df_directory = pd.read_csv(URL_DIRECTORY)

    expected_columns = (
        "Prénom",
        "Nom",
        "Téléphone",
        "Mobile",
        "Email",
        "Adresse",
    )
    for column in expected_columns:
        assert (
            column in df_directory.columns
        ), f"Column {column} not found in df_directory"
